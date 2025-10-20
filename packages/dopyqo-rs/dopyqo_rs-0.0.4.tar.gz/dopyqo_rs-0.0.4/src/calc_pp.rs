use itertools::Itertools;
use ndarray::Zip;
use ndarray_linalg::{Norm, Scalar};
use num_complex::Complex;
use numpy::ndarray::{s, Array1, Array2, Array3, Axis};
use numpy::{self as np, ToPyArray};
use ordered_float::OrderedFloat;
use pyo3::prelude::*;
use pyo3::{Bound, Python};
use rayon::prelude::*;
use rgsl::bessel as rgsl_bessel;
use scilib::math::basic::gamma;
use scilib::math::bessel;
use scilib::quantum::{spherical_harmonics, spherical_harmonics_theta_vec};
use std::cmp::Ordering;
// use std::collections::HashMap;
use hashbrown::HashMap;
use std::f64::consts::{FRAC_PI_2, PI, TAU}; // TAU = 2 PI

// Function to perform Simpson integration
fn simpson(y: &[f64], x: &[f64]) -> Result<f64, String> {
    // Handle case where ax and y are not of equal length
    if x.len() != y.len() {
        return Err("x and y must be of equal length".to_string());
    }

    // sum all x and y components using Composite simpson rule
    let mut integral: f64 = (0..x.len())
        // .into_par_iter()
        .map(|i| {
            if i == 0 || i == x.len() - 1 {
                y[i]
            } else if i % 2 == 0 {
                2.0 * y[i]
            } else {
                4.0 * y[i]
            }
        })
        .sum();
    // h = (b-a)/n, where n is number of sub intervals
    let h: f64 = (x[x.len() - 1] - x[0]) / (x.len() as f64 - 1.0);
    // append with 3/8 *h
    integral *= (1.0 / 3.0) * h;
    Ok(integral)
}

/// Function to calculate V_loc
/// V_loc(p, p') = \sum_I 4\pi/V e^{+i (p-p').R_I} [ \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - Z e^{-(p-p')^2/4}/(p-p')^2 ]
///              = V_loc(p - p')
///              = \sum_I 4\pi/V e^{+i (p-p').R_I} f(|p-p'|),
///              where f(|p-p'|) = \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - Z e^{-(p-p')^2/4}/(p-p')^2
/// if p = p', then V_{pp'} = g_zero_lim where g_zero_lim is the Fourier transform of V_loc(r) + Z/r for G=0, i.e.,
/// g_zero_lim = 4\pi/V int_0^\infty dr r^2 (V_loc(r) + Z/r) = 4\pi/V int_0^\infty dr r (r V_loc(r) + Z)
/// V_loc is first calculated on a equally spaced grid and then interpolated for each |p-p'| value.
/// This is a tiny bit slower than the hashmap implementation
#[pyfunction]
#[allow(clippy::too_many_arguments)]
pub fn v_loc_on_grid<'py>(
    py: Python<'py>,
    p_np: np::PyReadonlyArray2<f64>,             // shape (#waves, 3)
    c_ip_np: np::PyReadonlyArray2<Complex<f64>>, // shape (#bands, #waves)
    cell_volume: f64,
    atom_positions_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
    z_valence: f64,
    v_loc_r_np: np::PyReadonlyArray1<f64>,
    r_grid_np: np::PyReadonlyArray1<f64>,
    n_threads: usize,
) -> Bound<'py, np::PyArray2<Complex<f64>>> {
    if rayon::ThreadPoolBuilder::new()
        .num_threads(n_threads)
        .build_global()
        .is_err()
    {};

    let p = p_np.as_array();
    let c_ip = c_ip_np.as_array();
    let atom_positions = atom_positions_np.as_array();
    let v_loc_r = v_loc_r_np.as_array();
    let r_grid = r_grid_np.as_array().to_vec();

    let simpson_fn = simpson;

    // *2.0 to convert from Hartree to Rydberg since the PP is given in Rydberg atomic units
    let z_valence = z_valence * 2.0;

    let nwaves = p.len_of(Axis(0));
    let nbands = c_ip.len_of(Axis(0));
    // let nwaves = c_ip.len_of(Axis(1));
    // let natoms = atom_positions.len_of(Axis(0));

    // Division by two to convert from Rydberg to Hartree
    // since the PP is given in Rydberg atomic units
    let prefactor_scalar = 4.0 * PI / cell_volume / 2.0;

    // Fourier transform of V_loc(r) + Z/r for G=0
    let g_zero_lim = simpson_fn(
        &r_grid
            .iter()
            .zip(v_loc_r)
            .map(|(r, v_loc_r_val)| r * (r.mul_add(*v_loc_r_val, z_valence)))
            .collect_vec(),
        &r_grid,
    )
    .unwrap();

    let integrand_part = r_grid
        .iter()
        .zip(v_loc_r.iter())
        .map(|(r_val, v_loc_r_val)| {
            r_val.mul_add(*v_loc_r_val, z_valence * special::Error::error(*r_val))
        })
        .collect_vec();

    ////////// Interpolation like QE //////////
    // maximum momentum norm
    // times two since maximum norm of difference vector p-p' (|p-p'|) is
    //      twice the maximum norm of a momentum vector p (|p|), i.e.,
    //      max(|p-p'|) = 2 max(|p|)
    let qmax = 2.0
        * *p.axis_iter(Axis(0))
            .map(|p_vec| {
                OrderedFloat(
                    p_vec
                        .iter()
                        .map(|p_component| p_component.powi(2))
                        .sum::<f64>()
                        .sqrt(),
                )
            })
            .max()
            .unwrap();
    let dq = 0.01; // grid spacing
    let nq = (qmax / dq) as usize + 4; // + 1 + 3: +1 to have qmax in the grid, +3 to be able to interpolate up until qmax, because of 4-point Lagrance interpolation
    let mut v_loc_g_grid = Vec::with_capacity(nq);
    for i in 0..nq {
        let p_norm = (i as f64) * dq;

        let v_loc_g_val = {
            // Calculate integrands
            // shape (#r_values,)
            let integrand = r_grid
                .iter()
                .zip(integrand_part.iter())
                .map(|(r_val, int_val)| int_val * (p_norm * r_val).sin() / p_norm)
                .collect_vec();
            // Simpson integration minus Fourier transform of Z erf(r)/r
            (simpson_fn(&integrand, &r_grid.to_vec()).unwrap())
                - (z_valence * (-p_norm.powi(2) / 4.0).exp() / p_norm.powi(2))
        };

        v_loc_g_grid.push(v_loc_g_val);
    }

    // e^{-i p . R_I} as vec of vecs, outter vec len nwaves, inner vec len natoms
    //             OR as vec of ndarrays, vec len nwaves, ndarrays len natoms
    let struct_fact = p
        .axis_iter(Axis(0))
        .map(|p_vec| {
            atom_positions
                .axis_iter(Axis(0))
                .map(|pos_vec| {
                    // p . R_I
                    let exponent = p_vec.dot(&pos_vec);
                    // e^-ix = cos(x) - i sin(x)
                    exponent.cos() - Complex::i() * exponent.sin()
                })
                .collect::<Vec<Complex<f64>>>()
        })
        .collect::<Vec<Vec<Complex<f64>>>>();

    // a_pj = \sum_p' V_{pp'} c_{jp'}, V_{pp'} with row idx p and column idx p'
    // We need for one p every V_{pp'}
    //      V_loc(p, p') = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //                   = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //                   = 4\pi/V \int_0^\infty dr   (r V_loc(r)+Z erf(r)) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //                   = 4\pi/V \int_0^\infty dr   integrand_part(r)     sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //              multiple atoms
    //                   = prefactor_mat(p-p') [ \int_0^\infty dr integrand_part(r) sin(|p-p'| r)/|p-p'| - Z e^{-(p-p')^2/4}/(p-p')^2 ]
    //
    //      with prefactor_mat(p, p') = prefactor_mat(p-p') = \sum_I 4\pi/V e^{+i (p-p').R_I}
    let mut a_pj = Array2::<Complex<f64>>::default((nwaves, nbands));
    // let mut row = Array1::<Complex<f64>>::default((nwaves,)); // TODO: Comment with par_bridge
    a_pj.axis_iter_mut(Axis(0))
        // .into_par_iter()
        .zip(p.axis_iter(Axis(0)))
        .zip(&struct_fact)
        .enumerate()
        .par_bridge() // TODO: Uncomment with par_bridge
        .for_each(|(i, ((mut axis0, p_i), struct_fact_i))| {
            // TODO: Can we allocate row for each thread before hand?
            //       Probably needs more manual thread handling here, since we need the "index" of the thread
            let mut row = Array1::<Complex<f64>>::default((nwaves,)); // TODO: Uncomment with par_bridge

            // V_{pp'} for current row (momentum vector p=p_i), i.e.,
            // row is V_{pp'} for fixed p.
            // row(p') = V_p(p') where V_p(p') = V_{pp'}
            row.iter_mut()
                .zip(p.axis_iter(Axis(0)))
                .zip(&struct_fact)
                .enumerate()
                .for_each(|(j, ((val, p_j), struct_fact_j))| {
                    // prefactor_sum = \sum_I 4\pi/V e^{-i (p_i-p_j).R_I}
                    //               = \sum_I 4\pi/V e^{-i p_i . R_I} * e^{+i p_j.R_I}
                    //              != [ \sum_I 4\pi/V e^{-i p_i . R_I} ] * [ \sum_I 4\pi/V e^{+i p_j.R_I} ]
                    // with e^{-i (p_i-p_j).R_I} = e^{-i p_i . R_I} * e^{+i p_j.R_I} = e^{-i p_i . R_I} * e^{-i p_j.R_I}.conj()
                    let prefactor_sum = struct_fact_i
                        .iter()
                        .zip(struct_fact_j)
                        .map(|(term_i, term_j)| term_i * term_j.conj())
                        .sum::<Complex<f64>>()
                        * prefactor_scalar;

                    // p != p'
                    if i != j {
                        let p_norm = p_i
                            .iter()
                            .zip(&p_j)
                            .map(|(p_i_val, p_j_val)| (p_i_val - p_j_val).powi(2))
                            .sum::<f64>()
                            .sqrt();

                        let i0 = (p_norm / dq) as usize;
                        let i1 = i0 + 1;
                        let i2 = i0 + 2;
                        let i3 = i0 + 3;
                        // Using x_d = (x - x_0)/d
                        let x_d = p_norm / dq - (i0 as f64);
                        let x_d1 = x_d - 1.0;
                        let x_d2 = x_d - 2.0;
                        let x_d3 = x_d - 3.0;

                        // let res_val = v_loc_g_grid.get(i0).unwrap();
                        // Perform 4-point Lagrange interpolation
                        let res_val = -v_loc_g_grid[i0] * x_d1 * x_d2 * x_d3 / 6.0
                            + 0.5 * v_loc_g_grid[i1] * x_d * x_d2 * x_d3
                            - 0.5 * v_loc_g_grid[i2] * x_d * x_d1 * x_d3
                            + v_loc_g_grid[i3] * x_d * x_d1 * x_d2 / 6.0;
                        *val = prefactor_sum * res_val;
                    } else {
                        // p = p', then V_{pp'} = g_zero_lim
                        *val = prefactor_sum * g_zero_lim;
                    }
                });

            axis0.assign(&row.dot(&c_ip.t()));
        });

    (c_ip.map(|x| x.conj()).dot(&a_pj))
        .to_owned()
        .to_pyarray_bound(py)
}

/// Function to calculate the diagonal V_loc
/// V_loc(p, p') = \sum_I 4\pi/V e^{+i (p-p').R_I} [ \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - Z e^{-(p-p')^2/4}/(p-p')^2 ]
///              = V_loc(p - p')
///              = \sum_I 4\pi/V e^{+i (p-p').R_I} f(|p-p'|),
///              where f(|p-p'|) = \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - Z e^{-(p-p')^2/4}/(p-p')^2
/// if p = p', then V_{pp'} = g_zero_lim where g_zero_lim is the Fourier transform of V_loc(r) + Z/r for G=0, i.e.,
/// g_zero_lim = 4\pi/V int_0^\infty dr r^2 (V_loc(r) + Z/r) = 4\pi/V int_0^\infty dr r (r V_loc(r) + Z)
#[pyfunction]
#[allow(clippy::too_many_arguments)]
pub fn v_loc_diag_row_by_row<'py>(
    py: Python<'py>,
    p_np: np::PyReadonlyArray2<f64>,             // shape (#waves, 3)
    c_ip_np: np::PyReadonlyArray2<Complex<f64>>, // shape (#bands, #waves)
    cell_volume: f64,
    atom_positions_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
    z_valence: f64,
    v_loc_r_np: np::PyReadonlyArray1<f64>,
    r_grid_np: np::PyReadonlyArray1<f64>,
    n_threads: usize,
) -> Bound<'py, np::PyArray1<Complex<f64>>> {
    if rayon::ThreadPoolBuilder::new()
        .num_threads(n_threads)
        .build_global()
        .is_err()
    {};

    let p = p_np.as_array();
    let c_ip = c_ip_np.as_array();
    let atom_positions = atom_positions_np.as_array();
    let v_loc_r = v_loc_r_np.as_array();
    let r_grid = r_grid_np.as_array().to_vec();

    let simpson_fn = simpson;

    // *2.0 to convert from Hartree to Rydberg since the PP is given in Rydberg atomic units
    let z_valence = z_valence * 2.0;

    let nwaves = p.len_of(Axis(0));
    let nbands = c_ip.len_of(Axis(0));
    // let nwaves = c_ip.len_of(Axis(1));
    // let natoms = atom_positions.len_of(Axis(0));

    // Division by two to convert from Rydberg to Hartree
    // since the PP is given in Rydberg atomic units
    let prefactor_scalar = 4.0 * PI / cell_volume / 2.0;

    // Fourier transform of V_loc(r) + Z/r for G=0
    let g_zero_lim = simpson_fn(
        &r_grid
            .iter()
            .zip(v_loc_r)
            .map(|(r, v_loc_r_val)| r * (r.mul_add(*v_loc_r_val, z_valence)))
            .collect_vec(),
        &r_grid,
    )
    .unwrap();

    let integrand_part = r_grid
        .iter()
        .zip(v_loc_r.iter())
        .map(|(r_val, v_loc_r_val)| {
            r_val.mul_add(*v_loc_r_val, z_valence * special::Error::error(*r_val))
        })
        .collect_vec();

    // e^{-i p . R_I} as vec of vecs, outter vec len nwaves, inner vec len natoms
    //             OR as vec of ndarrays, vec len nwaves, ndarrays len natoms
    let struct_fact = p
        .axis_iter(Axis(0))
        .map(|p_vec| {
            atom_positions
                .axis_iter(Axis(0))
                .map(|pos_vec| {
                    // p . R_I
                    let exponent = p_vec.dot(&pos_vec);
                    // e^-ix = cos(x) - i sin(x)
                    exponent.cos() - Complex::i() * exponent.sin()
                })
                .collect::<Vec<Complex<f64>>>()
        })
        .collect::<Vec<Vec<Complex<f64>>>>();

    // a_pj = \sum_p' V_{pp'} c_{jp'}
    // V_{pp'} with row idx p and column idx p'.
    // We need for one p every V_{pp'}
    //      V_loc(p, p') = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //                   = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //                   = 4\pi/V \int_0^\infty dr   (r V_loc(r)+Z erf(r)) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //                   = 4\pi/V \int_0^\infty dr   integrand_part(r)     sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //              multiple atoms
    //                   = prefactor_mat(p-p') [ \int_0^\infty dr integrand_part(r) sin(|p-p'| r)/|p-p'| - Z e^{-(p-p')^2/4}/(p-p')^2 ]
    //
    //      with prefactor_mat(p, p') = prefactor_mat(p-p') = \sum_I 4\pi/V e^{+i (p-p').R_I}
    let mut a_pj = Array2::<Complex<f64>>::default((nwaves, nbands));
    let mut row = Array1::<Complex<f64>>::default((nwaves,));
    let mut p_norms_unique: HashMap<OrderedFloat<f64>, f64> = HashMap::new();
    a_pj.axis_iter_mut(Axis(0))
        // .into_par_iter()
        .zip(p.axis_iter(Axis(0)))
        .zip(&struct_fact)
        .enumerate()
        .for_each(|(i, ((mut axis0, p_i), struct_fact_i))| {
            // V_{pp'} for current row (momentum vector p=p_i), i.e.,
            // row is V_{pp'} for fixed p.
            // row(p') = V_p(p') where V_p(p') = V_{pp'}
            row.iter_mut()
                .zip(p.axis_iter(Axis(0)))
                .zip(&struct_fact)
                .enumerate()
                .for_each(|(j, ((val, p_j), struct_fact_j))| {
                    // prefactor_sum = \sum_I 4\pi/V e^{-i (p_i-p_j).R_I}
                    //               = \sum_I 4\pi/V e^{-i p_i . R_I} * e^{+i p_j.R_I}
                    //              != [ \sum_I 4\pi/V e^{-i p_i . R_I} ] * [ \sum_I 4\pi/V e^{+i p_j.R_I} ]
                    // with e^{-i (p_i-p_j).R_I} = e^{-i p_i . R_I} * e^{+i p_j.R_I} = e^{-i p_i . R_I} * e^{-i p_j.R_I}.conj()
                    let prefactor_sum = struct_fact_i
                        .iter()
                        .zip(struct_fact_j)
                        .map(|(term_i, term_j)| term_i * term_j.conj())
                        .sum::<Complex<f64>>()
                        * prefactor_scalar;

                    // p != p'
                    if i != j {
                        let p_norm = p_i
                            .iter()
                            .zip(&p_j)
                            .map(|(p_i_val, p_j_val)| (p_i_val - p_j_val).powi(2))
                            .sum::<f64>()
                            .sqrt();

                        let res_val =
                            p_norms_unique
                                .entry(OrderedFloat(p_norm))
                                .or_insert_with(|| {
                                    // Calculate integrands
                                    // shape (#r_values,)
                                    let integrand = r_grid
                                        .iter()
                                        .zip(integrand_part.iter())
                                        .map(|(r_val, int_val)| {
                                            int_val * (p_norm * r_val).sin() / p_norm
                                        })
                                        .collect_vec();
                                    // Simpson integration minus Fourier transform of Z erf(r)/r
                                    (simpson_fn(&integrand, &r_grid.to_vec()).unwrap())
                                        - (z_valence * (-p_norm.powi(2) / 4.0).exp()
                                            / p_norm.powi(2))
                                });
                        *val = prefactor_sum * *res_val;
                    } else {
                        // p = p', then V_{pp'} = g_zero_lim
                        *val = prefactor_sum * g_zero_lim;
                    }
                });

            axis0.assign(&row.dot(&c_ip.t()));
        });

    // We want to calculate <j|V|j> = \sum_pp' c_{jp} V_{pp'} c_{jp'} = \sum_p c_{jp} a_{pj}
    Zip::from(c_ip.rows())
        .and(a_pj.columns())
        .map_collect(|c_ip_row, a_pj_col| c_ip_row.map(|x| x.conj()).dot(&a_pj_col))
        .to_owned()
        .to_pyarray_bound(py)
}

/// Function to calculate V_loc
/// V_loc(p, p') = \sum_I 4\pi/V e^{+i (p-p').R_I} [ \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - Z e^{-(p-p')^2/4}/(p-p')^2 ]
///              = V_loc(p - p')
///              = \sum_I 4\pi/V e^{+i (p-p').R_I} f(|p-p'|),
///              where f(|p-p'|) = \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - Z e^{-(p-p')^2/4}/(p-p')^2
/// if p = p', then V_{pp'} = g_zero_lim where g_zero_lim is the Fourier transform of V_loc(r) + Z/r for G=0, i.e.,
/// g_zero_lim = 4\pi/V int_0^\infty dr r^2 (V_loc(r) + Z/r) = 4\pi/V int_0^\infty dr r (r V_loc(r) + Z)
#[pyfunction]
#[allow(clippy::too_many_arguments)]
pub fn v_loc_row_by_row_nohashmap_par<'py>(
    py: Python<'py>,
    p_np: np::PyReadonlyArray2<f64>,             // shape (#waves, 3)
    c_ip_np: np::PyReadonlyArray2<Complex<f64>>, // shape (#bands, #waves)
    cell_volume: f64,
    atom_positions_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
    z_valence: f64,
    v_loc_r_np: np::PyReadonlyArray1<f64>,
    r_grid_np: np::PyReadonlyArray1<f64>,
    n_threads: usize,
) -> Bound<'py, np::PyArray2<Complex<f64>>> {
    if rayon::ThreadPoolBuilder::new()
        .num_threads(n_threads)
        .build_global()
        .is_err()
    {};
    // rayon::ThreadPoolBuilder::new()
    //     .num_threads(n_threads)
    //     .build_global()
    //     .unwrap();

    let p = p_np.as_array();
    let c_ip = c_ip_np.as_array();
    let atom_positions = atom_positions_np.as_array();
    let v_loc_r = v_loc_r_np.as_array();
    let r_grid = r_grid_np.as_array().to_vec();

    let simpson_fn = simpson;

    // *2.0 to convert from Hartree to Rydberg since the PP is given in Rydberg atomic units
    let z_valence = z_valence * 2.0;

    let nwaves = p.len_of(Axis(0));
    let nbands = c_ip.len_of(Axis(0));
    // let nwaves = c_ip.len_of(Axis(1));
    // let natoms = atom_positions.len_of(Axis(0));

    // Division by two to convert from Rydberg to Hartree
    // since the PP is given in Rydberg atomic units
    let prefactor_scalar = 4.0 * PI / cell_volume / 2.0;

    // Fourier transform of V_loc(r) + Z/r for G=0
    let g_zero_lim = simpson_fn(
        &r_grid
            .iter()
            .zip(v_loc_r)
            .map(|(r, v_loc_r_val)| r * (r.mul_add(*v_loc_r_val, z_valence)))
            .collect_vec(),
        &r_grid,
    )
    .unwrap();

    let integrand_part = r_grid
        .iter()
        .zip(v_loc_r.iter())
        .map(|(r_val, v_loc_r_val)| {
            r_val.mul_add(*v_loc_r_val, z_valence * special::Error::error(*r_val))
        })
        .collect_vec();

    // // \sum_I e^{-i p . R_I}
    // let struct_fact = p
    //     .axis_iter(Axis(0))
    //     .map(|p_vec| {
    //         atom_positions
    //             .axis_iter(Axis(0))
    //             .map(|pos_vec| {
    //                 // p . R_I
    //                 let exponent = p_vec.dot(&pos_vec);
    //                 // e^-ix = cos(x) - i sin(x)
    //                 exponent.cos() - Complex::i() * exponent.sin()
    //             })
    //             .sum::<Complex<f64>>()
    //     })
    //     .collect::<Vec<Complex<f64>>>();

    // e^{-i p . R_I} as vec of vecs, outter vec len nwaves, inner vec len natoms
    //             OR as vec of ndarrays, vec len nwaves, ndarrays len natoms
    let struct_fact = p
        .axis_iter(Axis(0))
        .map(|p_vec| {
            atom_positions
                .axis_iter(Axis(0))
                .map(|pos_vec| {
                    // p . R_I
                    let exponent = p_vec.dot(&pos_vec);
                    // e^-ix = cos(x) - i sin(x)
                    exponent.cos() - Complex::i() * exponent.sin()
                })
                .collect::<Vec<Complex<f64>>>()
        })
        .collect::<Vec<Vec<Complex<f64>>>>();

    // a_pj = \sum_p' V_{pp'} c_{jp'}, V_{pp'} with row idx p and column idx p'
    // We need for one p every V_{pp'}
    //      V_loc(p, p') = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //                   = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //                   = 4\pi/V \int_0^\infty dr   (r V_loc(r)+Z erf(r)) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //                   = 4\pi/V \int_0^\infty dr   integrand_part(r)     sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //              multiple atoms
    //                   = prefactor_mat(p-p') [ \int_0^\infty dr integrand_part(r) sin(|p-p'| r)/|p-p'| - Z e^{-(p-p')^2/4}/(p-p')^2 ]
    //
    //      with prefactor_mat(p, p') = prefactor_mat(p-p') = \sum_I 4\pi/V e^{+i (p-p').R_I}
    let mut a_pj = Array2::<Complex<f64>>::default((nwaves, nbands));
    let mut row = Array1::<Complex<f64>>::default((nwaves,));
    let mut p_norms_unique: HashMap<OrderedFloat<f64>, f64> = HashMap::new();
    // let fs = FastSin::build(2);
    a_pj.axis_iter_mut(Axis(0))
        // .into_par_iter()
        .zip(p.axis_iter(Axis(0)))
        .zip(&struct_fact)
        .enumerate()
        .for_each(|(i, ((mut axis0, p_i), struct_fact_i))| {
            // V_{pp'} for current row (momentum vector p=p_i), i.e.,
            // row is V_{pp'} for fixed p.
            // row(p') = V_p(p') where V_p(p') = V_{pp'}
            row.iter_mut()
                .zip(p.axis_iter(Axis(0)))
                .zip(&struct_fact)
                .enumerate()
                .par_bridge()
                .for_each(|(j, ((val, p_j), struct_fact_j))| {
                    // prefactor_sum = \sum_I 4\pi/V e^{-i (p_i-p_j).R_I}
                    //               = \sum_I 4\pi/V e^{-i p_i . R_I} * e^{+i p_j.R_I}
                    //              != [ \sum_I 4\pi/V e^{-i p_i . R_I} ] * [ \sum_I 4\pi/V e^{+i p_j.R_I} ]
                    // with e^{-i (p_i-p_j).R_I} = e^{-i p_i . R_I} * e^{+i p_j.R_I} = e^{-i p_i . R_I} * e^{-i p_j.R_I}.conj()
                    let prefactor_sum = struct_fact_i
                        .iter()
                        .zip(struct_fact_j)
                        .map(|(term_i, term_j)| term_i * term_j.conj())
                        .sum::<Complex<f64>>()
                        * prefactor_scalar;

                    // p != p'
                    if i != j {
                        let p_norm = p_i
                            .iter()
                            .zip(&p_j)
                            .map(|(p_i_val, p_j_val)| (p_i_val - p_j_val).powi(2))
                            .sum::<f64>()
                            .sqrt();

                        let res_val = {
                            // Calculate integrands
                            // shape (#r_values,)
                            let integrand = r_grid
                                .iter()
                                .zip(integrand_part.iter())
                                .map(|(r_val, int_val)| int_val * (p_norm * r_val).sin() / p_norm)
                                .collect_vec();
                            // Simpson integration minus Fourier transform of Z erf(r)/r
                            (simpson_fn(&integrand, &r_grid.to_vec()).unwrap())
                                - (z_valence * (-p_norm.powi(2) / 4.0).exp() / p_norm.powi(2))
                        };
                        *val = prefactor_sum * res_val;
                    } else {
                        // p = p', then V_{pp'} = g_zero_lim
                        *val = prefactor_sum * g_zero_lim;
                    }
                });

            axis0.assign(&row.dot(&c_ip.t()));
        });

    (c_ip.map(|x| x.conj()).dot(&a_pj))
        .to_owned()
        .to_pyarray_bound(py)
}

/// Function to calculate V_loc
/// V_loc(p, p') = \sum_I 4\pi/V e^{+i (p-p').R_I} [ \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - Z e^{-(p-p')^2/4}/(p-p')^2 ]
///              = V_loc(p - p')
///              = \sum_I 4\pi/V e^{+i (p-p').R_I} f(|p-p'|),
///              where f(|p-p'|) = \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - Z e^{-(p-p')^2/4}/(p-p')^2
/// if p = p', then V_{pp'} = g_zero_lim where g_zero_lim is the Fourier transform of V_loc(r) + Z/r for G=0, i.e.,
/// g_zero_lim = 4\pi/V int_0^\infty dr r^2 (V_loc(r) + Z/r) = 4\pi/V int_0^\infty dr r (r V_loc(r) + Z)
#[pyfunction]
#[allow(clippy::too_many_arguments)]
pub fn v_loc_row_by_row<'py>(
    py: Python<'py>,
    p_np: np::PyReadonlyArray2<f64>,             // shape (#waves, 3)
    c_ip_np: np::PyReadonlyArray2<Complex<f64>>, // shape (#bands, #waves)
    cell_volume: f64,
    atom_positions_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
    z_valence: f64,
    v_loc_r_np: np::PyReadonlyArray1<f64>,
    r_grid_np: np::PyReadonlyArray1<f64>,
    n_threads: usize,
) -> Bound<'py, np::PyArray2<Complex<f64>>> {
    if rayon::ThreadPoolBuilder::new()
        .num_threads(n_threads)
        .build_global()
        .is_err()
    {};

    let p = p_np.as_array();
    let c_ip = c_ip_np.as_array();
    let atom_positions = atom_positions_np.as_array();
    let v_loc_r = v_loc_r_np.as_array();
    let r_grid = r_grid_np.as_array().to_vec();

    let simpson_fn = simpson;

    // *2.0 to convert from Hartree to Rydberg since the PP is given in Rydberg atomic units
    let z_valence = z_valence * 2.0;

    let nwaves = p.len_of(Axis(0));
    let nbands = c_ip.len_of(Axis(0));
    // let nwaves = c_ip.len_of(Axis(1));
    // let natoms = atom_positions.len_of(Axis(0));

    // Division by two to convert from Rydberg to Hartree
    // since the PP is given in Rydberg atomic units
    let prefactor_scalar = 4.0 * PI / cell_volume / 2.0;

    // Fourier transform of V_loc(r) + Z/r for G=0
    let g_zero_lim = simpson_fn(
        &r_grid
            .iter()
            .zip(v_loc_r)
            .map(|(r, v_loc_r_val)| r * (r.mul_add(*v_loc_r_val, z_valence)))
            .collect_vec(),
        &r_grid,
    )
    .unwrap();

    let integrand_part = r_grid
        .iter()
        .zip(v_loc_r.iter())
        .map(|(r_val, v_loc_r_val)| {
            r_val.mul_add(*v_loc_r_val, z_valence * special::Error::error(*r_val))
        })
        .collect_vec();

    // // \sum_I e^{-i p . R_I}
    // let struct_fact = p
    //     .axis_iter(Axis(0))
    //     .map(|p_vec| {
    //         atom_positions
    //             .axis_iter(Axis(0))
    //             .map(|pos_vec| {
    //                 // p . R_I
    //                 let exponent = p_vec.dot(&pos_vec);
    //                 // e^-ix = cos(x) - i sin(x)
    //                 exponent.cos() - Complex::i() * exponent.sin()
    //             })
    //             .sum::<Complex<f64>>()
    //     })
    //     .collect::<Vec<Complex<f64>>>();

    // e^{-i p . R_I} as vec of vecs, outter vec len nwaves, inner vec len natoms
    //             OR as vec of ndarrays, vec len nwaves, ndarrays len natoms
    let struct_fact = p
        .axis_iter(Axis(0))
        .map(|p_vec| {
            atom_positions
                .axis_iter(Axis(0))
                .map(|pos_vec| {
                    // p . R_I
                    let exponent = p_vec.dot(&pos_vec);
                    // e^-ix = cos(x) - i sin(x)
                    exponent.cos() - Complex::i() * exponent.sin()
                })
                .collect::<Vec<Complex<f64>>>()
        })
        .collect::<Vec<Vec<Complex<f64>>>>();

    // a_pj = \sum_p' V_{pp'} c_{jp'}, V_{pp'} with row idx p and column idx p'
    // We need for one p every V_{pp'}
    //      V_loc(p, p') = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //                   = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //                   = 4\pi/V \int_0^\infty dr   (r V_loc(r)+Z erf(r)) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //                   = 4\pi/V \int_0^\infty dr   integrand_part(r)     sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    //              multiple atoms
    //                   = prefactor_mat(p-p') [ \int_0^\infty dr integrand_part(r) sin(|p-p'| r)/|p-p'| - Z e^{-(p-p')^2/4}/(p-p')^2 ]
    //
    //      with prefactor_mat(p, p') = prefactor_mat(p-p') = \sum_I 4\pi/V e^{+i (p-p').R_I}
    let mut a_pj = Array2::<Complex<f64>>::default((nwaves, nbands));
    let mut row = Array1::<Complex<f64>>::default((nwaves,));
    let mut p_norms_unique: HashMap<OrderedFloat<f64>, f64> = HashMap::new();
    a_pj.axis_iter_mut(Axis(0))
        // .into_par_iter()
        .zip(p.axis_iter(Axis(0)))
        .zip(&struct_fact)
        .enumerate()
        // .par_bridge()
        .for_each(|(i, ((mut axis0, p_i), struct_fact_i))| {
            // V_{pp'} for current row (momentum vector p=p_i), i.e.,
            // row is V_{pp'} for fixed p.
            // row(p') = V_p(p') where V_p(p') = V_{pp'}
            row.iter_mut()
                .zip(p.axis_iter(Axis(0)))
                .zip(&struct_fact)
                .enumerate()
                .for_each(|(j, ((val, p_j), struct_fact_j))| {
                    // prefactor_sum = \sum_I 4\pi/V e^{-i (p_i-p_j).R_I}
                    //               = \sum_I 4\pi/V e^{-i p_i . R_I} * e^{+i p_j.R_I}
                    //              != [ \sum_I 4\pi/V e^{-i p_i . R_I} ] * [ \sum_I 4\pi/V e^{+i p_j.R_I} ]
                    // with e^{-i (p_i-p_j).R_I} = e^{-i p_i . R_I} * e^{+i p_j.R_I} = e^{-i p_i . R_I} * e^{-i p_j.R_I}.conj()
                    let prefactor_sum = struct_fact_i
                        .iter()
                        .zip(struct_fact_j)
                        .map(|(term_i, term_j)| term_i * term_j.conj())
                        .sum::<Complex<f64>>()
                        * prefactor_scalar;

                    // p != p'
                    if i != j {
                        let p_norm = p_i
                            .iter()
                            .zip(&p_j)
                            .map(|(p_i_val, p_j_val)| (p_i_val - p_j_val).powi(2))
                            .sum::<f64>()
                            .sqrt();

                        let res_val =
                            p_norms_unique
                                .entry(OrderedFloat(p_norm))
                                .or_insert_with(|| {
                                    // Calculate integrands
                                    // shape (#r_values,)
                                    let integrand = r_grid
                                        .iter()
                                        .zip(integrand_part.iter())
                                        .map(|(r_val, int_val)| {
                                            int_val * (p_norm * r_val).sin() / p_norm
                                        })
                                        .collect_vec();
                                    // Simpson integration minus Fourier transform of Z erf(r)/r
                                    (simpson_fn(&integrand, &r_grid.to_vec()).unwrap())
                                        - (z_valence * (-p_norm.powi(2) / 4.0).exp()
                                            / p_norm.powi(2))
                                });
                        *val = prefactor_sum * *res_val;
                    } else {
                        // p = p', then V_{pp'} = g_zero_lim
                        *val = prefactor_sum * g_zero_lim;
                    }
                });

            axis0.assign(&row.dot(&c_ip.t()));
        });

    (c_ip.map(|x| x.conj()).dot(&a_pj))
        .to_owned()
        .to_pyarray_bound(py)
}

/// Function to calculate V_loc
/// V_loc(p, p') = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
#[pyfunction]
#[allow(clippy::too_many_arguments)]
pub fn v_loc_pw_unique<'py>(
    py: Python<'py>,
    p_np: np::PyReadonlyArray2<f64>, // shape (#waves, 3)
    cell_volume: f64,
    atom_positions_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
    z_valence: f64,
    v_loc_r_np: np::PyReadonlyArray1<f64>,
    r_grid_np: np::PyReadonlyArray1<f64>,
    n_threads: usize,
) -> Bound<'py, np::PyArray2<Complex<f64>>> {
    if rayon::ThreadPoolBuilder::new()
        .num_threads(n_threads)
        .build_global()
        .is_err()
    {};

    let p = p_np.as_array();
    let atom_positions = atom_positions_np.as_array();
    let v_loc_r = v_loc_r_np.as_array();
    let r_grid = r_grid_np.as_array().to_vec();

    let simpson_fn = simpson;

    // *2.0 to convert from Hartree to Rydberg since the PP is given in Rydberg atomic units
    let z_valence = z_valence * 2.0;

    let nwaves = p.len_of(Axis(0));
    // let natoms = atom_positions.len_of(Axis(0));

    // Division by two to convert from Rydberg to Hartree
    // since the PP is given in Rydberg atomic units
    let prefactor_scalar = 4.0 * PI / cell_volume / 2.0;

    // Fourier transform of V_loc(r) + Z/r for G=0
    let g_zero_lim = simpson_fn(
        &r_grid
            .iter()
            .zip(v_loc_r)
            .map(|(r, v_loc_r_val)| r * (r.mul_add(*v_loc_r_val, z_valence)))
            .collect_vec(),
        &r_grid,
    )
    .unwrap();

    let integrand_part = r_grid
        .iter()
        .zip(v_loc_r.iter())
        .map(|(r_val, v_loc_r_val)| {
            r_val.mul_add(*v_loc_r_val, z_valence * special::Error::error(*r_val))
        })
        .collect_vec();

    // let p_i_dot_pos_mat = Array2::<f64>::from_shape_fn((natoms, nwaves), |(i, j)| {
    //     let atom_i_pos = atom_positions.slice(s![i, ..]);
    //     let p_j = p.slice(s![j, ..]);
    //     p_j.dot(&atom_i_pos)
    // });
    // let mut prefactor_mat =
    //     Array2::<Complex<f64>>::from_elem((nwaves, nwaves), Complex::new(prefactor_scalar, 0.0));
    // prefactor_mat
    //     .axis_iter_mut(Axis(0))
    //     .into_par_iter()
    //     .zip(p_i_dot_pos_mat.axis_iter(Axis(1)))
    //     .for_each(|(mut axis0, dot_i)| {
    //         axis0
    //             .iter_mut()
    //             .zip(p_i_dot_pos_mat.axis_iter(Axis(1)))
    //             .for_each(|(val, dot_j)| {
    //                 let prefactor_sum = (&dot_i - &dot_j)
    //                     .map(|dot_diff| (-Complex::i() * dot_diff).exp())
    //                     .sum();
    //                 *val *= prefactor_sum;
    //             })
    //     });

    // \sum_I 4\pi/V e^{+i (p-p').R_I}
    let mut prefactor_mat =
        Array2::<Complex<f64>>::from_elem((nwaves, nwaves), Complex::new(prefactor_scalar, 0.0));
    // Use parallel iteration for the outer loop
    prefactor_mat
        .axis_iter_mut(Axis(0))
        .into_par_iter()
        .zip(p.axis_iter(Axis(0)))
        .for_each(|(mut axis0, p_i)| {
            axis0
                .iter_mut()
                .zip(p.axis_iter(Axis(0)))
                .for_each(|(val, p_j)| {
                    let prefactor_sum = atom_positions
                        .axis_iter(Axis(0))
                        .map(|pos_vec| {
                            let exponent = p_i.dot(&pos_vec) - p_j.dot(&pos_vec);
                            // e^-ix = cos(x) - i sin(x)
                            exponent.cos() - Complex::i() * exponent.sin()
                            // (-Complex::i() * (p_i.dot(&pos_vec) - p_j.dot(&pos_vec))).exp()
                        })
                        .sum::<Complex<f64>>();

                    *val *= prefactor_sum;
                })
        });

    //////////////////////////////////////////////////
    // Direct computation during HashMap generation //
    //////////////////////////////////////////////////
    // V_loc(p, p') = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin((p-p')r)/(p-p') - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
    // Not parrallelizable since we modify the Hashmap p_norms_unique inside the loop
    // Using par_iter over res_mat and using DashMap does not improve performance
    // let mut p_norms_unique: DashMap<OrderedFloat<f64>, f64> = DashMap::new();
    // NOTE: Iterating over all matrix elements (let p_head = p;) is not significantly
    //       slower than iterating only over the upper/lower diagonal of res_mat
    //       and setting res_mat[[j, i]]=res_mat[[i, j]] (py/rs speedup: 3.35 vs 3.67)
    let mut p_norms_unique: HashMap<OrderedFloat<f64>, f64> = HashMap::new();
    let mut res_mat = prefactor_mat;
    for (i, p_i) in p.rows().into_iter().enumerate() {
        let (p_head, _p_tail) = p.split_at(Axis(0), i + 1);
        // let p_head = p;
        for (j, p_j) in p_head.rows().into_iter().enumerate() {
            if i != j {
                let p_norm = p_i
                    .iter()
                    .zip(&p_j)
                    .map(|(p_i_val, p_j_val)| (p_i_val - p_j_val).powi(2))
                    .sum::<f64>()
                    .sqrt();

                let res_val = p_norms_unique
                    .entry(OrderedFloat(p_norm))
                    .or_insert_with(|| {
                        // Calculate integrands
                        // shape (#r_values,)
                        let integrand = r_grid
                            .iter()
                            .zip(integrand_part.iter())
                            .map(|(r_val, int_val)| int_val * (p_norm * r_val).sin() / p_norm)
                            .collect_vec();
                        // Simpson integration minus Fourier transform of Z erf(r)/r
                        (simpson_fn(&integrand, &r_grid.to_vec()).unwrap())
                            - (z_valence * (-p_norm.powi(2) / 4.0).exp() / p_norm.powi(2))
                    });
                res_mat[[i, j]] *= *res_val;
                res_mat[[j, i]] *= *res_val;
            } else {
                res_mat[[i, j]] *= g_zero_lim
            }
        }
    }

    // let res_mat = Array2::<Complex<f64>>::from_shape_fn((nwaves, nwaves), |(i, j)| {
    //     let p_norm = p
    //         .row(i)
    //         .iter()
    //         .zip(p.row(j))
    //         .map(|(p_i_val, p_j_val)| (p_i_val - p_j_val).powi(2))
    //         .sum::<f64>()
    //         .sqrt();

    //     if i != j {
    //         let res_val = p_norms_unique
    //             .entry(OrderedFloat(p_norm))
    //             .or_insert_with(|| {
    //                 // Calculate integrands
    //                 // shape (#r_values,)
    //                 let integrand = r_grid
    //                     .iter()
    //                     .zip(integrand_part.iter())
    //                     .map(|(r_val, int_val)| int_val * (p_norm * r_val).sin() / p_norm)
    //                     .collect_vec();
    //                 // Simpson integration minus Fourier transform of Z erf(r)/r
    //                 (simpson_fn(&integrand, &r_grid.to_vec()).unwrap())
    //                     - (z_valence * (-p_norm.powi(2) / 4.0).exp() / p_norm.powi(2))
    //             });
    //         *res_val * prefactor_mat[[i, j]]
    //     } else {
    //         g_zero_lim * prefactor_mat[[i, j]]
    //     }
    // });

    res_mat.to_owned().to_pyarray_bound(py)
}

// Function to calculate g_zero_lim
#[pyfunction]
pub fn calc_g_zero_lim(
    integrand_np: np::PyReadonlyArray1<f64>,
    z_valence: f64,
    v_loc_r_np: np::PyReadonlyArray1<f64>,
    r_grid_np: np::PyReadonlyArray1<f64>,
) -> f64 {
    let v_loc_r = v_loc_r_np.as_array();
    let r_grid = r_grid_np.as_array();

    let integrand_py = integrand_np.as_array();

    let simpson_fn = simpson;

    // *2.0 to convert from Hartree to Rydberg since the PP is given in Rydberg atomic units
    let z_valence = z_valence * 2.0;

    // Fourier transform of V_loc(r) + Z/r for G=0
    let g_zero_lim = simpson_fn(
        &r_grid
            .iter()
            .zip(v_loc_r)
            .map(|(r, v_val)| r * (r * v_val + z_valence))
            .collect_vec(),
        &r_grid.to_vec(),
    )
    .unwrap();

    // let int_domain = integraal::DomainDescriptor::Explicit(r_grid.to_vec());
    // let int_function = integraal::FunctionDescriptor::Values(
    //     r_grid
    //         .iter()
    //         .zip(v_loc_r)
    //         .map(|(r, v_val)| r * (r * v_val + z_valence))
    //         .collect_vec(),
    // );
    // let int_method = integraal::ComputeMethod::Trapezoid;
    // let g_zero_lim = integraal::Integraal::default()
    //     .domain(int_domain)
    //     .function(int_function)
    //     .method(int_method)
    //     .compute()
    //     .unwrap();

    // Bound::new(py, g_zero_lim).unwrap()
    g_zero_lim
}

// Function to calculate the prefactor matrix
#[pyfunction]
pub fn calc_prefactor_mat<'py>(
    py: Python<'py>,
    p_np: np::PyReadonlyArray2<f64>, // shape (#waves, 3)
    cell_volume: f64,
    atom_positions_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
) -> Bound<'py, np::PyArray2<Complex<f64>>> {
    let p = p_np.as_array();
    let atom_positions = atom_positions_np.as_array();

    let nwaves = p.len_of(Axis(0));
    let natoms = atom_positions.len_of(Axis(0));

    // Division by two to convert from Rydberg to Hartree
    // since the PP is given in Rydberg atomic units
    let prefactor_scalar = 4.0 * PI / cell_volume / 2.0;

    // \sum_I 4\pi/V e^{+i (p-p').R_I}
    let mut prefactor_mat = Array2::<Complex<f64>>::default((nwaves, nwaves));
    for i in 0..nwaves {
        for j in 0..nwaves {
            // let p_minus_p_prime = p.slice(s![i, ..]).to_owned() - p.slice(s![j, ..]);
            // if i == j {
            //     prefactor_mat[[i, j]] = Complex::new(prefactor_scalar, 0.0);
            //     continue;
            // }

            let p_minus_p_prime =
                Array1::from_shape_fn(3, |coord_idx| p[[i, coord_idx]] - p[[j, coord_idx]]);

            // \sum_I 4\pi/V e^{+i (p-p').R_I}
            prefactor_mat[[i, j]] = Complex::new(prefactor_scalar, 0.0)
                * (0..natoms)
                    .map(|atom_idx| {
                        (-Complex::i()
                            //(p-p').R_I
                            * p_minus_p_prime.dot(&atom_positions.slice(s![atom_idx, ..])))
                        .exp()
                    })
                    .sum::<Complex<f64>>();
        }
    }

    prefactor_mat.to_owned().to_pyarray_bound(py)
}

/// Function to calculate V_nl
/// Calculates the matrix of the non-local pseudopotential in the Kohn-Sham basis in Hartree atomic units
/// V_nl(p, p') = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I) \sum_{lm} \sum_{ij} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) D_{ij} F^j_l(G')
///             = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I) \sum_{ij} D_{ij} \sum_{lm} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) F^j_l(G')
/// where
///     F^i_l(G) = \int dr r^2 \beta^i_l(r) j_l(Gr)
/// where j_l(x) is the spherical Bessel function
#[pyfunction]
#[allow(clippy::too_many_arguments)]
pub fn v_nl_row_by_row<'py>(
    py: Python<'py>,
    p_np: np::PyReadonlyArray2<f64>,             // shape (#waves, 3)
    c_ip_np: np::PyReadonlyArray2<Complex<f64>>, // shape (#bands, #waves)
    cell_volume: f64,
    atom_positions_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
    r_grid_np: np::PyReadonlyArray1<f64>,
    d_ij_np: np::PyReadonlyArray2<f64>,
    beta_projector_idx_list: Vec<i64>,
    beta_projector_angular_momentum_list: Vec<usize>,
    beta_projector_values_list_np: Vec<np::PyReadonlyArray1<f64>>,
    n_threads: usize,
    // ) -> HashMap<usize, Bound<'py, np::PyArray2<f64>>> {
) -> Bound<'py, np::PyArray2<Complex<f64>>> {
    if rayon::ThreadPoolBuilder::new()
        .num_threads(n_threads)
        .build_global()
        .is_err()
    {};

    let p = p_np.as_array();
    let c_ip = c_ip_np.as_array();
    let atom_positions = atom_positions_np.as_array();
    let r_grid = r_grid_np.as_array();
    let d_ij = d_ij_np.as_array();
    let beta_projector_values_list = beta_projector_values_list_np
        .iter()
        .map(|x| x.as_array())
        .collect_vec();

    let n_beta_proj = beta_projector_idx_list.len();

    let simpson_fn = simpson;

    let nwaves = p.len_of(Axis(0));
    let nbands = c_ip.len_of(Axis(0));
    // let nwaves = c_ip.len_of(Axis(1));

    // Use coordinates -x, z, -y (convention used in Quantum ESPRESSO) instead of x, y, z
    let mut p_cart = p.select(Axis(1), &[0, 2, 1]); // xyz to xzy
    p_cart.rows_mut().into_iter().for_each(|mut row| {
        row[0] *= -1.0; // to -x, z, y
        row[2] *= -1.0; // to -x, z, -y
    });

    cart_to_sph_for_inplace(&mut p_cart);
    let p_sph = p_cart; // Rename
    let p_r = p_sph.slice(s![.., 0]);
    let p_theta = p_sph.slice(s![.., 1]);
    let p_phi = p_sph.slice(s![.., 2]);

    // f_il_g = f_i(g) = \int dr r^2 \beta^i_l(r) j_l(gr)
    // Note that l is uniquely defined by i, so l=l_i and
    // f_il_g only depends on i and g
    let mut f_il_g = Array2::<f64>::default((n_beta_proj, nwaves));

    let mut bessel_hashmap: HashMap<usize, Array2<f64>> = HashMap::new();
    let mut integrand_buffer = vec![0.0; r_grid.len()];
    for l_val in beta_projector_angular_momentum_list.iter() {
        bessel_hashmap.entry(*l_val).or_insert_with(|| {
            let l_val = *l_val as i32;

            Array2::<f64>::from_shape_fn((r_grid.len(), nwaves), |(i, j)| {
                let r_val = r_grid[i];
                let p_r_val = p_r[j];
                r_val * rgsl_bessel::jl(l_val, r_val * p_r_val)
            })
        });
    }

    for i in 0..n_beta_proj {
        let l_val = &beta_projector_angular_momentum_list[i];
        let bessel_arr = bessel_hashmap.get(l_val).unwrap();
        for j in 0..nwaves {
            integrand_buffer
                .iter_mut()
                .zip(&beta_projector_values_list[i])
                .enumerate()
                .for_each(|(r_idx, (int_val, bp_val))| {
                    *int_val = bp_val * bessel_arr[[r_idx, j]];
                });
            f_il_g[[i, j]] = simpson_fn(&integrand_buffer, &r_grid.to_vec()).unwrap();
        }
    }

    // // Precompute spherical harmonics Y_{lm}(G) and Y*_{lm}(G')
    // // let y_lm_g = Vec::<Array2<f64>>::with_capacity(beta_projector_angular_momentum_list.len());
    // let mut y_lm_g: HashMap<usize, Array2<f64>> = HashMap::new();
    // // let mut y_lm_g: HashMap<usize, Vec<f64>> = HashMap::new();
    // beta_projector_angular_momentum_list
    //     .iter()
    //     .for_each(|&l_val| {
    //         y_lm_g.entry(l_val).or_insert_with(|| {
    //             Array2::<f64>::from_shape_fn((l_val * 2 + 1, nwaves), |(i, j)| {
    //                 let m = i as isize - l_val as isize;
    //                 let sph_harm_val = spherical_harmonics(l_val, m, p_theta[j], p_phi[j]);
    //                 match m.cmp(&0) {
    //                     Ordering::Less => (2.0).sqrt() * (-1.0).powi(m as i32) * sph_harm_val.im,
    //                     Ordering::Greater => (2.0).sqrt() * (-1.0).powi(m as i32) * sph_harm_val.re,
    //                     Ordering::Equal => sph_harm_val.re,
    //                 }
    //             })
    //         });
    //     });
    // let l_max = y_lm_g.keys().max().unwrap();

    let mut y_lm_g = Vec::<Array2<f64>>::with_capacity(beta_projector_angular_momentum_list.len());
    let l_max = beta_projector_angular_momentum_list.iter().max().unwrap();
    for l_val in 0..l_max + 1 {
        y_lm_g.push({
            Array2::<f64>::from_shape_fn((l_val * 2 + 1, nwaves), |(i, j)| {
                let m = i as isize - l_val as isize;
                let sph_harm_val = spherical_harmonics(l_val, m, p_theta[j], p_phi[j]);
                match m.cmp(&0) {
                    Ordering::Less => (2.0).sqrt() * (-1.0).powi(m as i32) * sph_harm_val.im,
                    Ordering::Greater => (2.0).sqrt() * (-1.0).powi(m as i32) * sph_harm_val.re,
                    Ordering::Equal => sph_harm_val.re,
                }
            })
        });
    }

    // prefactor_scalar = (4\pi)^2/V
    // Division by two to convert from Rydberg to Hartree
    // since the PP is given in Rydberg atomic units
    let prefactor_scalar = (4.0 * PI).powi(2) / cell_volume / 2.0;

    // // \sum_I e^{-i p . R_I}
    // let struct_fact = p
    //     .axis_iter(Axis(0))
    //     .map(|p_vec| {
    //         atom_positions
    //             .axis_iter(Axis(0))
    //             .map(|pos_vec| {
    //                 // p . R_I
    //                 let exponent = p_vec.dot(&pos_vec);
    //                 // e^-ix = cos(x) - i sin(x)
    //                 exponent.cos() - Complex::i() * exponent.sin()
    //             })
    //             .sum::<Complex<f64>>()
    //     })
    //     .collect::<Vec<Complex<f64>>>();

    // TODO: Check performance hit due to more complex calculation of structure factor
    //       since the previous calculation was wrong!

    // e^{-i p . R_I} as vec of vecs, outter vec len nwaves, inner vec len natoms
    //             OR as vec of ndarrays, vec len nwaves, ndarrays len natoms
    let struct_fact = p
        .axis_iter(Axis(0))
        .map(|p_vec| {
            atom_positions
                .axis_iter(Axis(0))
                .map(|pos_vec| {
                    // p . R_I
                    let exponent = p_vec.dot(&pos_vec);
                    // e^-ix = cos(x) - i sin(x)
                    exponent.cos() - Complex::i() * exponent.sin()
                })
                .collect::<Vec<Complex<f64>>>()
        })
        .collect::<Vec<Vec<Complex<f64>>>>();

    // a_pj = \sum_p' V_{pp'} c_{jp'}, V_{pp'} with row idx p and column idx p'
    // We need for one p every V_{pp'}
    //
    // V_nl(p, p') = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I) \sum_{lm} \sum_{ij} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) D_{ij} F^j_l(G')
    //             = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I) \sum_{ij} D_{ij} \sum_{lm} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) F^j_l(G')
    //             = prefactor_mat(p-p')                   \sum_{ij} D_{ij} \sum_{lm} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) F^j_l(G')
    //
    //      with prefactor_mat(p, p') = prefactor_mat(p-p') = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I)
    let mut a_pj = Array2::<Complex<f64>>::default((nwaves, nbands));
    let mut row = Array1::<Complex<f64>>::default((nwaves,));
    let mut m_sums_vec: Vec<f64> = vec![0.0; *l_max + 1];
    a_pj.axis_iter_mut(Axis(0))
        // .into_par_iter()
        .zip(f_il_g.axis_iter(Axis(1)))
        .zip(&struct_fact)
        .enumerate()
        .for_each(|(i, ((mut axis0, f_il_g_col_i), struct_fact_i))| {
            // V_{pp'} for current row (momentum vector p=p_i), i.e.,
            // row is V_{pp'} for fixed p.
            // row(p') = V_p(p') where V_p(p') = V_{pp'}
            row.iter_mut()
                .zip(f_il_g.axis_iter(Axis(1)))
                .zip(&struct_fact)
                .enumerate()
                .for_each(|(j, ((val, f_il_g_col_j), struct_fact_j))| {
                    let prefactor_sum = struct_fact_i
                        .iter()
                        .zip(struct_fact_j)
                        .map(|(term_i, term_j)| term_i * term_j.conj())
                        .sum::<Complex<f64>>()
                        * prefactor_scalar;

                    // // m_sums(l)(p, p') = \sum_m Y_lm(p) Y*_lm(p')
                    // for (l_val, y_lm_g_mat) in y_lm_g.iter() {
                    //     let mut m_sum_val = 0.0;
                    //     // y_lm_g_row is Y_lm(p) for a specific m, we iterate over all m here.
                    //     for y_lm_g_row in y_lm_g_mat.rows() {
                    //         // For a specific m we want Y_lm(p) for a specific p
                    //         m_sum_val += y_lm_g_row[i] * y_lm_g_row[j].conj();
                    //     }

                    //     // Equivalent to above but slower
                    //     // let m_sum_val = y_lm_g_mat.column(i).dot(&y_lm_g_mat.column(j));

                    //     m_sums_vec[*l_val] = m_sum_val;
                    // }

                    // m_sums(l)(p, p') = \sum_m Y_lm(p) Y*_lm(p')
                    for (y_lm_g_mat, m_sum_val) in y_lm_g.iter().zip(m_sums_vec.iter_mut()) {
                        *m_sum_val = 0.0;
                        // y_lm_g_row is Y_lm(p) for a specific m, we iterate over all m here.
                        for y_lm_g_row in y_lm_g_mat.rows() {
                            // For a specific m we want Y_lm(p) for a specific p
                            *m_sum_val += y_lm_g_row[i] * y_lm_g_row[j].conj();
                        }
                    }

                    // Explicit loop is slower

                    // Loop through d_ij and angular momentum pairs
                    let res_val: f64 = beta_projector_angular_momentum_list
                        .iter()
                        .enumerate()
                        .cartesian_product(beta_projector_angular_momentum_list.iter().enumerate())
                        .filter(|((_, l_i), (_, l_j))| l_i == l_j)
                        .map(|((l_i_idx, l_i), (l_j_idx, _l_j))| {
                            d_ij[[l_i_idx, l_j_idx]]
                                // * f_il_g[[l_j_idx, j]]
                                * f_il_g_col_j[l_j_idx]
                                // * f_il_g[[l_i_idx, i]]
                                * f_il_g_col_i[l_i_idx]
                                * m_sums_vec[*l_i]
                        })
                        .sum();

                    *val = prefactor_sum * res_val;
                });

            axis0.assign(&row.dot(&c_ip.t()));
        });

    (c_ip.map(|x| x.conj()).dot(&a_pj))
        .to_owned()
        .to_pyarray_bound(py)
    // (c_ip.dot(&a_pj)).to_owned().to_pyarray_bound(py)
}

/// Function to calculate V_nl
/// Calculates the matrix of the non-local pseudopotential in the Kohn-Sham basis in Hartree atomic units
/// V_nl(p, p') = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I) \sum_{lm} \sum_{ij} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) D_{ij} F^j_l(G')
///             = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I) \sum_{ij} D_{ij} \sum_{lm} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) F^j_l(G')
/// where
///     F^i_l(G) = \int dr r^2 \beta^i_l(r) j_l(Gr)
/// where j_l(x) is the spherical Bessel function
#[pyfunction]
#[allow(clippy::too_many_arguments)]
pub fn v_nl_row_by_row_par<'py>(
    py: Python<'py>,
    p_np: np::PyReadonlyArray2<f64>,             // shape (#waves, 3)
    c_ip_np: np::PyReadonlyArray2<Complex<f64>>, // shape (#bands, #waves)
    cell_volume: f64,
    atom_positions_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
    r_grid_np: np::PyReadonlyArray1<f64>,
    d_ij_np: np::PyReadonlyArray2<f64>,
    beta_projector_idx_list: Vec<i64>,
    beta_projector_angular_momentum_list: Vec<usize>,
    beta_projector_values_list_np: Vec<np::PyReadonlyArray1<f64>>,
    n_threads: usize,
    // ) -> HashMap<usize, Bound<'py, np::PyArray2<f64>>> {
) -> Bound<'py, np::PyArray2<Complex<f64>>> {
    if rayon::ThreadPoolBuilder::new()
        .num_threads(n_threads)
        .build_global()
        .is_err()
    {};

    let p = p_np.as_array();
    let c_ip = c_ip_np.as_array();
    let atom_positions = atom_positions_np.as_array();
    let r_grid = r_grid_np.as_array();
    let d_ij = d_ij_np.as_array();
    let beta_projector_values_list = beta_projector_values_list_np
        .iter()
        .map(|x| x.as_array())
        .collect_vec();

    let n_beta_proj = beta_projector_idx_list.len();

    let simpson_fn = simpson;

    let nwaves = p.len_of(Axis(0));
    let nbands = c_ip.len_of(Axis(0));
    // let nwaves = c_ip.len_of(Axis(1));

    // Use coordinates -x, z, -y (convention used in Quantum ESPRESSO) instead of x, y, z
    let mut p_cart = p.select(Axis(1), &[0, 2, 1]); // xyz to xzy
    p_cart.rows_mut().into_iter().for_each(|mut row| {
        row[0] *= -1.0; // to -x, z, y
        row[2] *= -1.0; // to -x, z, -y
    });

    cart_to_sph_for_inplace(&mut p_cart);
    let p_sph = p_cart; // Rename
    let p_r = p_sph.slice(s![.., 0]);
    let p_theta = p_sph.slice(s![.., 1]);
    let p_phi = p_sph.slice(s![.., 2]);

    // f_il_g = f_i(g) = \int dr r^2 \beta^i_l(r) j_l(gr)
    // Note that l is uniquely defined by i, so l=l_i and
    // f_il_g only depends on i and g
    let mut f_il_g = Array2::<f64>::default((n_beta_proj, nwaves));

    let mut bessel_hashmap: HashMap<usize, Array2<f64>> = HashMap::new();
    let mut integrand_buffer = vec![0.0; r_grid.len()];
    for l_val in beta_projector_angular_momentum_list.iter() {
        bessel_hashmap.entry(*l_val).or_insert_with(|| {
            let l_val = *l_val as i32;

            Array2::<f64>::from_shape_fn((r_grid.len(), nwaves), |(i, j)| {
                let r_val = r_grid[i];
                let p_r_val = p_r[j];
                r_val * rgsl_bessel::jl(l_val, r_val * p_r_val)
            })
        });
    }

    for i in 0..n_beta_proj {
        let l_val = &beta_projector_angular_momentum_list[i];
        let bessel_arr = bessel_hashmap.get(l_val).unwrap();
        for j in 0..nwaves {
            integrand_buffer
                .iter_mut()
                .zip(&beta_projector_values_list[i])
                .enumerate()
                .for_each(|(r_idx, (int_val, bp_val))| {
                    *int_val = bp_val * bessel_arr[[r_idx, j]];
                });
            f_il_g[[i, j]] = simpson_fn(&integrand_buffer, &r_grid.to_vec()).unwrap();
        }
    }

    let mut y_lm_g = Vec::<Array2<f64>>::with_capacity(beta_projector_angular_momentum_list.len());
    let l_max = beta_projector_angular_momentum_list.iter().max().unwrap();
    for l_val in 0..l_max + 1 {
        y_lm_g.push({
            Array2::<f64>::from_shape_fn((l_val * 2 + 1, nwaves), |(i, j)| {
                let m = i as isize - l_val as isize;
                let sph_harm_val = spherical_harmonics(l_val, m, p_theta[j], p_phi[j]);
                match m.cmp(&0) {
                    Ordering::Less => (2.0).sqrt() * (-1.0).powi(m as i32) * sph_harm_val.im,
                    Ordering::Greater => (2.0).sqrt() * (-1.0).powi(m as i32) * sph_harm_val.re,
                    Ordering::Equal => sph_harm_val.re,
                }
            })
        });
    }

    let prefactor_scalar = (4.0 * PI).powi(2) / cell_volume / 2.0;

    // e^{-i p . R_I} as vec of vecs, outter vec len nwaves, inner vec len natoms
    //             OR as vec of ndarrays, vec len nwaves, ndarrays len natoms
    let struct_fact = p
        .axis_iter(Axis(0))
        .map(|p_vec| {
            atom_positions
                .axis_iter(Axis(0))
                .map(|pos_vec| {
                    // p . R_I
                    let exponent = p_vec.dot(&pos_vec);
                    // e^-ix = cos(x) - i sin(x)
                    exponent.cos() - Complex::i() * exponent.sin()
                })
                .collect::<Vec<Complex<f64>>>()
        })
        .collect::<Vec<Vec<Complex<f64>>>>();

    // a_pj = \sum_p' V_{pp'} c_{jp'}, V_{pp'} with row idx p and column idx p'
    // We need for one p every V_{pp'}
    //
    // V_nl(p, p') = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I) \sum_{lm} \sum_{ij} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) D_{ij} F^j_l(G')
    //             = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I) \sum_{ij} D_{ij} \sum_{lm} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) F^j_l(G')
    //             = prefactor_mat(p-p')                   \sum_{ij} D_{ij} \sum_{lm} Y_{lm}(G) Y*_{lm}(G') F^i_l(G) F^j_l(G')
    //
    //      with prefactor_mat(p, p') = prefactor_mat(p-p') = (4\pi)^2/V \sum_I e^(-i (p-p') . R_I)
    let mut a_pj = Array2::<Complex<f64>>::default((nwaves, nbands));
    a_pj.axis_iter_mut(Axis(0))
        // .into_par_iter()
        .zip(f_il_g.axis_iter(Axis(1)))
        .zip(&struct_fact)
        .enumerate()
        .par_bridge()
        .for_each(|(i, ((mut axis0, f_il_g_col_i), struct_fact_i))| {
            let mut row = Array1::<Complex<f64>>::default((nwaves,));
            let mut m_sums_vec: Vec<f64> = vec![0.0; *l_max + 1];

            // V_{pp'} for current row (momentum vector p=p_i), i.e.,
            // row is V_{pp'} for fixed p.
            // row(p') = V_p(p') where V_p(p') = V_{pp'}
            row.iter_mut()
                .zip(f_il_g.axis_iter(Axis(1)))
                .zip(&struct_fact)
                .enumerate()
                .for_each(|(j, ((val, f_il_g_col_j), struct_fact_j))| {
                    let prefactor_sum = struct_fact_i
                        .iter()
                        .zip(struct_fact_j)
                        .map(|(term_i, term_j)| term_i * term_j.conj())
                        .sum::<Complex<f64>>()
                        * prefactor_scalar;

                    // m_sums(l)(p, p') = \sum_m Y_lm(p) Y*_lm(p')
                    for (y_lm_g_mat, m_sum_val) in y_lm_g.iter().zip(m_sums_vec.iter_mut()) {
                        *m_sum_val = 0.0;
                        // y_lm_g_row is Y_lm(p) for a specific m, we iterate over all m here.
                        for y_lm_g_row in y_lm_g_mat.rows() {
                            // For a specific m we want Y_lm(p) for a specific p
                            *m_sum_val += y_lm_g_row[i] * y_lm_g_row[j].conj();
                        }
                    }

                    // Loop through d_ij and angular momentum pairs
                    let res_val: f64 = beta_projector_angular_momentum_list
                        .iter()
                        .enumerate()
                        .cartesian_product(beta_projector_angular_momentum_list.iter().enumerate())
                        .filter(|((_, l_i), (_, l_j))| l_i == l_j)
                        .map(|((l_i_idx, l_i), (l_j_idx, _l_j))| {
                            d_ij[[l_i_idx, l_j_idx]]
                                // * f_il_g[[l_j_idx, j]]
                                * f_il_g_col_j[l_j_idx]
                                // * f_il_g[[l_i_idx, i]]
                                * f_il_g_col_i[l_i_idx]
                                * m_sums_vec[*l_i]
                        })
                        .sum();

                    *val = prefactor_sum * res_val;
                });

            axis0.assign(&row.dot(&c_ip.t()));
        });

    (c_ip.map(|x| x.conj()).dot(&a_pj))
        .to_owned()
        .to_pyarray_bound(py)
}

// Function to calculate V_nl
#[pyfunction]
#[allow(clippy::too_many_arguments)]
pub fn v_nl_pw<'py>(
    py: Python<'py>,
    p_np: np::PyReadonlyArray2<f64>, // shape (#waves, 3)
    cell_volume: f64,
    atom_positions_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
    r_grid_np: np::PyReadonlyArray1<f64>,
    d_ij_np: np::PyReadonlyArray2<f64>,
    beta_projector_idx_list: Vec<i64>,
    beta_projector_angular_momentum_list: Vec<usize>,
    beta_projector_values_list_np: Vec<np::PyReadonlyArray1<f64>>,
    n_threads: usize,
    // ) -> HashMap<usize, Bound<'py, np::PyArray2<f64>>> {
) -> Bound<'py, np::PyArray2<Complex<f64>>> {
    if rayon::ThreadPoolBuilder::new()
        .num_threads(n_threads)
        .build_global()
        .is_err()
    {};

    let p = p_np.as_array();
    let atom_positions = atom_positions_np.as_array();
    let r_grid = r_grid_np.as_array();
    let d_ij = d_ij_np.as_array();
    let beta_projector_values_list = beta_projector_values_list_np
        .iter()
        .map(|x| x.as_array())
        .collect_vec();

    let n_beta_proj = beta_projector_idx_list.len();

    let simpson_fn = simpson;

    let nwaves = p.len_of(Axis(0));

    // Division by two to convert from Rydberg to Hartree
    // since the PP is given in Rydberg atomic units
    let prefactor_scalar = (4.0 * PI).powi(2) / cell_volume / 2.0;

    // \sum_I 4\pi/V e^{+i (p-p').R_I}
    let mut prefactor_mat =
        Array2::<Complex<f64>>::from_elem((nwaves, nwaves), Complex::new(prefactor_scalar, 0.0));
    // Use parallel iteration for the outer loop
    prefactor_mat
        .axis_iter_mut(Axis(0))
        .into_par_iter()
        .zip(p.axis_iter(Axis(0)))
        .for_each(|(mut axis0, p_i)| {
            axis0
                .iter_mut()
                .zip(p.axis_iter(Axis(0)))
                .for_each(|(val, p_j)| {
                    let prefactor_sum = atom_positions
                        .axis_iter(Axis(0))
                        .map(|pos_vec| {
                            let exponent = p_i.dot(&pos_vec) - p_j.dot(&pos_vec);
                            // e^-ix = cos(x) - i sin(x)
                            exponent.cos() - Complex::i() * exponent.sin()
                            // (-Complex::i() * (p_i.dot(&pos_vec) - p_j.dot(&pos_vec))).exp()
                        })
                        .sum::<Complex<f64>>();

                    *val *= prefactor_sum;
                })
        });

    // Use coordinates -x, z, -y (convention used in Quantum ESPRESSO) instead of x, y, z
    let mut p_cart = p.select(Axis(1), &[0, 2, 1]); // xyz to xzy
    p_cart.rows_mut().into_iter().for_each(|mut row| {
        row[0] *= -1.0; // to -x, z, y
        row[2] *= -1.0; // to -x, z, -y
    });

    cart_to_sph_for_inplace(&mut p_cart);
    let p_sph = p_cart; // Rename
    let p_r = p_sph.slice(s![.., 0]);
    let p_theta = p_sph.slice(s![.., 1]);
    let p_phi = p_sph.slice(s![.., 2]);

    // f_il_g = f_i(g) = \int dr r^2 \beta^i_l(r) j_l(gr)
    // Note that l is uniquely defined by i, so l=l_i and
    // f_il_g only depends on i and g
    let mut f_il_g = Array2::<f64>::default((n_beta_proj, nwaves));

    let mut bessel_hashmap: HashMap<usize, Array2<f64>> = HashMap::new();
    let mut integrand_buffer = vec![0.0; r_grid.len()];
    for l_val in beta_projector_angular_momentum_list.iter() {
        bessel_hashmap.entry(*l_val).or_insert_with(|| {
            let l_val = *l_val as i32;

            Array2::<f64>::from_shape_fn((r_grid.len(), nwaves), |(i, j)| {
                let r_val = r_grid[i];
                let p_r_val = p_r[j];
                r_val * rgsl_bessel::jl(l_val, r_val * p_r_val)
            })
        });
    }

    for i in 0..n_beta_proj {
        let l_val = &beta_projector_angular_momentum_list[i];
        let bessel_arr = bessel_hashmap.get(l_val).unwrap();
        for j in 0..nwaves {
            integrand_buffer
                .iter_mut()
                .zip(&beta_projector_values_list[i])
                .enumerate()
                .for_each(|(r_idx, (int_val, bp_val))| {
                    *int_val = bp_val * bessel_arr[[r_idx, j]];
                });
            f_il_g[[i, j]] = simpson_fn(&integrand_buffer, &r_grid.to_vec()).unwrap();
        }
    }

    // let mut f_il_g = Array2::<f64>::default((n_beta_proj, nwaves));
    // f_il_g
    //     .axis_iter_mut(ndarray::Axis(1))
    //     .zip(p_r)
    //     .for_each(|(mut col, p_r_val)| {
    //         for i in 0..n_beta_proj {
    //             // Precompute the angular momentum index.
    //             let l_val = beta_projector_angular_momentum_list[i] as i32;

    //             // Compute the integrand values, reusing the buffer.
    //             for (k, (&r_val, &bp_val)) in r_grid
    //                 .iter()
    //                 .zip(&beta_projector_values_list[i])
    //                 .enumerate()
    //             {
    //                 integrand_buffer[k] = r_val * bp_val * rgsl_bessel::jl(l_val, r_val * p_r_val);
    //             }

    //             // Perform integration using Simpson's rule.
    //             col[i] = simpson_fn(&integrand_buffer, &r_grid.to_vec()).unwrap();
    //         }
    //     });

    // This works:
    // let mut integrand_buffer = vec![0.0; r_grid.len()];
    // for j in 0..nwaves {
    //     let p_r_val = p_r[j];
    //     for i in 0..n_beta_proj {
    //         // Compute the integrand values, reusing the buffer.
    //         let l_val = beta_projector_angular_momentum_list[i] as i32;
    //         integrand_buffer
    //             .iter_mut()
    //             .zip(r_grid)
    //             .zip(&beta_projector_values_list[i])
    //             .for_each(|((int_val, r_val), bp_val)| {
    //                 *int_val = r_val * bp_val * rgsl_bessel::jl(l_val, r_val * p_r_val);
    //             });
    //         f_il_g[[i, j]] = simpson_fn(&integrand_buffer, &r_grid.to_vec()).unwrap();
    //     }
    // }

    // for ((mut f_il_g_row, l_val), bp_values) in f_il_g
    //     .axis_iter_mut(Axis(0))
    //     .zip(beta_projector_angular_momentum_list.iter())
    //     .zip(beta_projector_values_list.iter())
    // {
    //     for (f_il_g_val, p_r_val) in f_il_g_row.iter_mut().zip(p_r) {
    //         let integrand = r_grid
    //             .iter()
    //             .zip(bp_values)
    //             .map(|(r_val, bp_val)| {
    //                 // Bessel function of real positive number is real
    //                 r_val
    //                     * bp_val
    //                     * bessel::sj_nu(*l_val as f64, Complex::new(*r_val * p_r_val, 0.0)).re
    //             })
    //             .collect();
    //         *f_il_g_val = simpson_fn(&integrand, &r_grid.to_vec()).unwrap();
    //     }
    // }

    // Precompute spherical harmonics Y_{lm}(G) and Y*_{lm}(G')
    // let y_lm_g = Vec::<Array2<f64>>::with_capacity(beta_projector_angular_momentum_list.len());
    let mut y_lm_g: HashMap<usize, Array2<f64>> = HashMap::new();
    // let mut y_lm_g: HashMap<usize, Vec<f64>> = HashMap::new();
    beta_projector_angular_momentum_list
        .iter()
        .for_each(|&l_val| {
            y_lm_g.entry(l_val).or_insert_with(|| {
                // FIXME: m_sum goes over Y_lm(p) Y_lm(p') so two different p values.
                //        Here we would only calculate the diagonal entries p=p'
                // p_theta
                //     .iter()
                //     .zip(p_phi.iter())
                //     .map(|(p_theta_val, p_phi_val)| {
                //         (-(l_val as isize)..=(l_val as isize))
                //             .map(|m| {
                //                 let sph_harm_val =
                //                     spherical_harmonics(l_val, m, *p_theta_val, *p_phi_val);

                //                 match m.cmp(&0) {
                //                     Ordering::Less => {
                //                         (2.0).sqrt() * (-1.0).powi(m as i32) * sph_harm_val.im
                //                     }
                //                     Ordering::Greater => {
                //                         (2.0).sqrt() * (-1.0).powi(m as i32) * sph_harm_val.re
                //                     }
                //                     Ordering::Equal => sph_harm_val.re,
                //                 }
                //             })
                //             .sum::<f64>()
                //     })
                //     .collect_vec()

                Array2::<f64>::from_shape_fn((l_val * 2 + 1, nwaves), |(i, j)| {
                    let m = i as isize - l_val as isize;
                    let sph_harm_val = spherical_harmonics(l_val, m, p_theta[j], p_phi[j]);
                    match m.cmp(&0) {
                        Ordering::Less => (2.0).sqrt() * (-1.0).powi(m as i32) * sph_harm_val.im,
                        Ordering::Greater => (2.0).sqrt() * (-1.0).powi(m as i32) * sph_harm_val.re,
                        Ordering::Equal => sph_harm_val.re,
                    }
                })
            });
        });

    // m_sums(l)(p, p') = \sum_m Y_lm(p) Y*_lm(p')
    let mut m_sums: HashMap<usize, Array2<f64>> =
        HashMap::with_capacity(*beta_projector_angular_momentum_list.iter().max().unwrap());
    for (l_val, y_lm_g_mat) in y_lm_g.iter() {
        let mut m_sum_mat = Array2::<f64>::default((nwaves, nwaves));
        // y_lm_g_row is Y_lm(p) for a specific m, we iterate over all m here.
        for y_lm_g_row in y_lm_g_mat.rows() {
            for i in 0..nwaves {
                for j in 0..nwaves {
                    m_sum_mat[[i, j]] += y_lm_g_row[i] * y_lm_g_row[j].conj()
                }
            }
        }

        m_sums.insert(*l_val, m_sum_mat);
    }

    // let mut v_nl_mat = prefactor_mat;
    let mut v_nl_mat = Array2::<f64>::default((nwaves, nwaves));
    // Loop through d_ij and angular momentum pairs
    for (i, l_i) in beta_projector_angular_momentum_list.iter().enumerate() {
        for (j, l_j) in beta_projector_angular_momentum_list.iter().enumerate() {
            if l_i != l_j {
                continue;
            }
            let m_sums_mat = m_sums.get(l_i).unwrap();
            v_nl_mat
                .axis_iter_mut(Axis(0))
                .enumerate()
                // .into_par_iter()
                .for_each(|(p_idx, mut axis0)| {
                    let f_il_p_val = f_il_g[[i, p_idx]];

                    axis0.iter_mut().enumerate().for_each(|(p_prime_idx, val)| {
                        // let prefactor_sum = atom_positions
                        //     .axis_iter(Axis(0))
                        //     .map(|pos_vec| {
                        //         let exponent =
                        //             p.row(p_idx).dot(&pos_vec) - p.row(p_prime_idx).dot(&pos_vec);
                        //         // e^-ix = cos(x) - i sin(x)
                        //         exponent.cos() - Complex::i() * exponent.sin()
                        //         // (-Complex::i() * (p_i.dot(&pos_vec) - p_j.dot(&pos_vec))).exp()
                        //     })
                        //     .sum::<Complex<f64>>();

                        // beta_projector_angular_momentum_list.iter().zip(f_il_p)

                        // let m_sums_val = y_lm_g[l_i]
                        //     .column(p_idx)
                        //     .dot(&y_lm_g[l_i].column(p_prime_idx));

                        *val += d_ij[[i, j]]
                            * f_il_g[[j, p_prime_idx]]
                            * f_il_p_val
                            * m_sums_mat[[p_idx, p_prime_idx]];

                        // *val *= prefactor_sum * prefactor_scalar;
                    })
                });
        }
    }

    Zip::from(&mut prefactor_mat)
        .and(&v_nl_mat)
        .par_for_each(|pref_val, mat_val| {
            *pref_val *= mat_val;
        });

    prefactor_mat.to_pyarray_bound(py)
}











//NOTE: WORK IN PROGRESS

/// Function to calculate the force of V_loc
// #[pyfunction]
// #[allow(clippy::too_many_arguments)]
// pub fn v_loc_force_on_grid<'py>(
//     py: Python<'py>,
//     p_np: np::PyReadonlyArray2<f64>,             // shape (#waves, 3)
//     c_ip_np: np::PyReadonlyArray2<Complex<f64>>, // shape (#bands, #waves)
//     cell_volume: f64,
//     atom_positions_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
//     z_valence: f64,
//     v_loc_r_np: np::PyReadonlyArray1<f64>,
//     r_grid_np: np::PyReadonlyArray1<f64>,
//     n_threads: usize,
// ) -> Bound<'py, np::PyArray2<Complex<f64>>> {
//     if rayon::ThreadPoolBuilder::new()
//         .num_threads(n_threads)
//         .build_global()
//         .is_err()
//     {};

//     let p = p_np.as_array();
//     let c_ip = c_ip_np.as_array();
//     let atom_positions = atom_positions_np.as_array();
//     let v_loc_r = v_loc_r_np.as_array();
//     let r_grid = r_grid_np.as_array().to_vec();

//     let simpson_fn = simpson;

//     // *2.0 to convert from Hartree to Rydberg since the PP is given in Rydberg atomic units
//     let z_valence = z_valence * 2.0;

//     let nwaves = p.len_of(Axis(0));
//     let nbands = c_ip.len_of(Axis(0));
//     // let nwaves = c_ip.len_of(Axis(1));
//     // let natoms = atom_positions.len_of(Axis(0));

//     // Division by two to convert from Rydberg to Hartree
//     // since the PP is given in Rydberg atomic units
//     let prefactor_scalar = 4.0 * PI / cell_volume / 2.0;

//     // Fourier transform of V_loc(r) + Z/r for G=0
//     let g_zero_lim = simpson_fn(
//         &r_grid
//             .iter()
//             .zip(v_loc_r)
//             .map(|(r, v_loc_r_val)| r * (r.mul_add(*v_loc_r_val, z_valence)))
//             .collect_vec(),
//         &r_grid,
//     )
//     .unwrap();

//     let integrand_part = r_grid
//         .iter()
//         .zip(v_loc_r.iter())
//         .map(|(r_val, v_loc_r_val)| {
//             r_val.mul_add(*v_loc_r_val, z_valence * special::Error::error(*r_val))
//         })
//         .collect_vec();

//     ////////// Interpolation like QE //////////
//     // maximum momentum norm
//     // times two since maximum norm of difference vector p-p' (|p-p'|) is
//     //      twice the maximum norm of a momentum vector p (|p|), i.e.,
//     //      max(|p-p'|) = 2 max(|p|)
//     let qmax = 2.0
//         * *p.axis_iter(Axis(0))
//             .map(|p_vec| {
//                 OrderedFloat(
//                     p_vec
//                         .iter()
//                         .map(|p_component| p_component.powi(2))
//                         .sum::<f64>()
//                         .sqrt(),
//                 )
//             })
//             .max()
//             .unwrap();
//     let dq = 0.01; // grid spacing
//     let nq = (qmax / dq) as usize + 4; // + 1 + 3: +1 to have qmax in the grid, +3 to be able to interpolate up until qmax, because of 4-point Lagrance interpolation
//     let mut v_loc_g_grid = Vec::with_capacity(nq);
//     for i in 0..nq {
//         let p_norm = (i as f64) * dq;

//         let v_loc_g_val = {
//             // Calculate integrands
//             // shape (#r_values,)
//             let integrand = r_grid
//                 .iter()
//                 .zip(integrand_part.iter())
//                 .map(|(r_val, int_val)| int_val * (p_norm * r_val).sin() / p_norm)
//                 .collect_vec();
//             // Simpson integration minus Fourier transform of Z erf(r)/r
//             (simpson_fn(&integrand, &r_grid.to_vec()).unwrap())
//                 - (z_valence * (-p_norm.powi(2) / 4.0).exp() / p_norm.powi(2))
//         };

//         v_loc_g_grid.push(v_loc_g_val);
//     }

//     // e^{-i p . R_I} as vec of vecs, outter vec len nwaves, inner vec len natoms
//     //             OR as vec of ndarrays, vec len nwaves, ndarrays len natoms
//     let struct_fact = p
//         .axis_iter(Axis(0))
//         .map(|p_vec| {
//             atom_positions
//                 .axis_iter(Axis(0))
//                 .map(|pos_vec| {
//                     // p . R_I
//                     let exponent = p_vec.dot(&pos_vec);
//                     // e^-ix = cos(x) - i sin(x)
//                     exponent.cos() - Complex::i() * exponent.sin()
//                 })
//                 .collect::<Vec<Complex<f64>>>()
//         })
//         .collect::<Vec<Vec<Complex<f64>>>>();

//     // a_pj = \sum_p' V_{pp'} c_{jp'}, V_{pp'} with row idx p and column idx p'
//     // We need for one p every V_{pp'}
//     //      V_loc(p, p') = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
//     //                   = 4\pi/V \int_0^\infty dr r (V_loc(r)+Z erf(r)/r) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
//     //                   = 4\pi/V \int_0^\infty dr   (r V_loc(r)+Z erf(r)) sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
//     //                   = 4\pi/V \int_0^\infty dr   integrand_part(r)     sin(|p-p'| r)/|p-p'| - 4\pi/V Z e^{-(p-p')^2/4}/(p-p')^2
//     //              multiple atoms
//     //                   = prefactor_mat(p-p') [ \int_0^\infty dr integrand_part(r) sin(|p-p'| r)/|p-p'| - Z e^{-(p-p')^2/4}/(p-p')^2 ]
//     //
//     //      with prefactor_mat(p, p') = prefactor_mat(p-p') = \sum_I 4\pi/V e^{+i (p-p').R_I}
//     let mut a_pj = Array2::<Complex<f64>>::default((nwaves, nbands));
//     // let mut row = Array1::<Complex<f64>>::default((nwaves,)); // TODO: Comment with par_bridge
//     a_pj.axis_iter_mut(Axis(0))
//         // .into_par_iter()
//         .zip(p.axis_iter(Axis(0)))
//         .zip(&struct_fact)
//         .enumerate()
//         .par_bridge() // TODO: Uncomment with par_bridge
//         .for_each(|(i, ((mut axis0, p_i), struct_fact_i))| {
//             // TODO: Can we allocate row for each thread before hand?
//             //       Probably needs more manual thread handling here, since we need the "index" of the thread
//             let mut row = Array1::<Complex<f64>>::default((nwaves,)); // TODO: Uncomment with par_bridge

//             // V_{pp'} for current row (momentum vector p=p_i), i.e.,
//             // row is V_{pp'} for fixed p.
//             // row(p') = V_p(p') where V_p(p') = V_{pp'}
//             row.iter_mut()
//                 .zip(p.axis_iter(Axis(0)))
//                 .zip(&struct_fact)
//                 .enumerate()
//                 .for_each(|(j, ((val, p_j), struct_fact_j))| {
//                     // prefactor_sum = \sum_I 4\pi/V e^{-i (p_i-p_j).R_I}
//                     //               = \sum_I 4\pi/V e^{-i p_i . R_I} * e^{+i p_j.R_I}
//                     //              != [ \sum_I 4\pi/V e^{-i p_i . R_I} ] * [ \sum_I 4\pi/V e^{+i p_j.R_I} ]
//                     // with e^{-i (p_i-p_j).R_I} = e^{-i p_i . R_I} * e^{+i p_j.R_I} = e^{-i p_i . R_I} * e^{-i p_j.R_I}.conj()
//                     let prefactor_sum = struct_fact_i
//                         .iter()
//                         .zip(struct_fact_j)
//                         .map(|(term_i, term_j)| term_i * term_j.conj())
//                         .sum::<Complex<f64>>()
//                         * prefactor_scalar;

//                     // p != p'
//                     if i != j {
//                         let p_norm = p_i
//                             .iter()
//                             .zip(&p_j)
//                             .map(|(p_i_val, p_j_val)| (p_i_val - p_j_val).powi(2))
//                             .sum::<f64>()
//                             .sqrt();

//                         let i0 = (p_norm / dq) as usize;
//                         let i1 = i0 + 1;
//                         let i2 = i0 + 2;
//                         let i3 = i0 + 3;
//                         // Using x_d = (x - x_0)/d
//                         let x_d = p_norm / dq - (i0 as f64);
//                         let x_d1 = x_d - 1.0;
//                         let x_d2 = x_d - 2.0;
//                         let x_d3 = x_d - 3.0;

//                         // let res_val = v_loc_g_grid.get(i0).unwrap();
//                         // Perform 4-point Lagrange interpolation
//                         let res_val = -v_loc_g_grid[i0] * x_d1 * x_d2 * x_d3 / 6.0
//                             + 0.5 * v_loc_g_grid[i1] * x_d * x_d2 * x_d3
//                             - 0.5 * v_loc_g_grid[i2] * x_d * x_d1 * x_d3
//                             + v_loc_g_grid[i3] * x_d * x_d1 * x_d2 / 6.0;
//                         *val = prefactor_sum * res_val;
//                     } else {
//                         // p = p', then V_{pp'} = g_zero_lim
//                         *val = prefactor_sum * g_zero_lim;
//                     }
//                 });

//             axis0.assign(&row.dot(&c_ip.t()));
//         });

//     (c_ip.map(|x| x.conj()).dot(&a_pj))
//         .to_owned()
//         .to_pyarray_bound(py)
// }




// Function to convert a set of 3D Cartesian coordinates to spherical coordinates
pub fn cart_to_sph_for_inplace(xyz: &mut Array2<f64>) {
    xyz.rows_mut().into_iter().for_each(|mut cart_vec| {
        let xy = cart_vec[0].powi(2) + cart_vec[1].powi(2);
        let r = cart_vec.norm_l2();
        let theta = xy.sqrt().atan2(cart_vec[2]);
        let mut phi = cart_vec[1].atan2(cart_vec[0]);
        if phi < 0.0 {
            phi += TAU;
        }

        cart_vec[0] = r;
        cart_vec[1] = theta;
        cart_vec[2] = phi;
    });
}
