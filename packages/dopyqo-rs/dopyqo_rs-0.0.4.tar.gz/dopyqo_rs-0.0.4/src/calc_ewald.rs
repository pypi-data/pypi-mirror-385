use std::f64::consts::PI;

use itertools::Itertools;
use ndarray_linalg::{Norm, Scalar};
use num_complex::Complex;
use numpy::{self as np, ToPyArray};
use numpy::ndarray::Array1;
use ordered_float::OrderedFloat;
use pyo3::prelude::*;
use pyo3::{Bound, Python};

/// Straightforwad unoptimized implementation for calculating the Ewald energy
#[pyfunction]
#[allow(clippy::too_many_arguments)]
pub fn ewald(
    atom_positions_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
    atomic_numbers_np: np::PyReadonlyArray1<i64>, // shape (#atoms, 3)
    lattice_vectors_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
    lattice_vectors_reciprocal_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
    cell_volume: f64,
    gcutrho: f64,
    sigma: f64,
    // n_threads: usize,
) -> f64 {
    // if rayon::ThreadPoolBuilder::new()
    //     .num_threads(n_threads)
    //     .build_global()
    //     .is_err()
    // {};

    let atom_positions = atom_positions_np.as_array();
    let atomic_numbers = atomic_numbers_np.as_array();
    let lattice_vectors = lattice_vectors_np.as_array();
    let lattice_vectors_reciprocal = lattice_vectors_reciprocal_np.as_array();

    let alat = lattice_vectors.row(0).norm_l2();
    let t_vec_max_norm = 4.0 / sigma.sqrt() / alat;
    let b_norms = lattice_vectors_reciprocal
        .rows()
        .into_iter()
        .map(|row| row.norm_l2())
        .collect_vec();
    let (n_max_x, n_max_y, n_max_z) = b_norms
        .iter()
        .map(|b_norm| (b_norm * t_vec_max_norm) as i64 + 2)
        .collect_tuple()
        .unwrap();

    let t_vecs_unordered = (-n_max_x..=n_max_x)
        .cartesian_product(-n_max_y..=n_max_y)
        .cartesian_product(-n_max_z..=n_max_z)
        .map(|((nx, ny), nz)| {
            (
                lattice_vectors.dot(&Array1::from_vec(vec![nx as f64, ny as f64, nz as f64])),
                (nx, ny, nz),
            )
        });

    // let t_vecs = t_vecs_unordered
    //     .sorted_by(|a, b| Ord::cmp(&OrderedFloat(b.0.norm_l2()), &OrderedFloat(a.0.norm_l2())))
    //     .collect_vec();
    // println!("INSPECTING t_vecs");
    // let _ = t_vecs
    //     .iter()
    //     .take(20)
    //     .inspect(|x| println!("{:?}", x))
    //     .collect_vec();
    // println!("DONE INSPECTING!\n\n\n\n");

    const EPS: f64 = 1e-8;

    let mut converged_real = false;
    let mut e_short = 0.0;
    for (t_vec, (nx, ny, nz)) in t_vecs_unordered
        .sorted_by(|a, b| Ord::cmp(&OrderedFloat(a.0.norm_l2()), &OrderedFloat(b.0.norm_l2())))
    {
        for (i, pos_i) in atom_positions.rows().into_iter().enumerate() {
            let z_i = atomic_numbers.get(i).unwrap();
            for (j, pos_j) in atom_positions.rows().into_iter().enumerate() {
                if t_vec.iter().all(|&x| x.abs() < EPS) && i == j {
                    continue;
                }
                let z_j = atomic_numbers.get(j).unwrap();
                let r = (pos_i.to_owned() - pos_j - &t_vec).norm_l2();
                e_short += (z_i * z_j) as f64 * special::Error::compl_error(r * sigma.sqrt()) / r;

                // with this choice terms up to ZiZj*erfc(4) are counted (erfc(4)=1.5e-8)
                if r >= 4.0 / sigma.sqrt() {
                    // Stopping real-sum
                    converged_real = true;
                    // break
                } else {
                    // println!("{} {}", e_short, t_vec);
                }
            }
        }
        // if converged_real {
        //     break;
        // }
    }
    e_short *= 0.5;

    // Estimate size of Miller indices grid using the cutoff-energy and reciprocal lattice vectors
    // A simple, but not accurate enough, estimate would be gcutrho/|b_i| for i \in {1, 2, 3}
    // Here we take the shape of the reciprocal lattice into account:
    //       max[ gcutrho/(|b_i| + \sum_{j \neq i} b_i . b_j ) ] for i \in {1, 2, 3}
    let mut e_long = 0.0;
    let b1 = lattice_vectors_reciprocal.row(0);
    let b2 = lattice_vectors_reciprocal.row(1);
    let b3 = lattice_vectors_reciprocal.row(2);
    let k_max = [
        (gcutrho / (b1.norm_l2() + b1.dot(&b2) + b1.dot(&b3)))
            .abs()
            .round() as i64,
        (gcutrho / (b2.norm_l2() + b2.dot(&b1) + b2.dot(&b3)))
            .abs()
            .round() as i64,
        (gcutrho / (b3.norm_l2() + b3.dot(&b1) + b3.dot(&b2)))
            .abs()
            .round() as i64,
    ]
    .iter()
    .max()
    .unwrap()
    .to_owned();

    // let k_max = (gcutrho * 2.0).round() as i64;
    for kx in -k_max..=k_max {
        for ky in -k_max..=k_max {
            for kz in -k_max..=k_max {
                if kx == 0 && ky == 0 && kz == 0 {
                    continue;
                }
                let k_vec = lattice_vectors_reciprocal
                    .t()
                    .dot(&Array1::from_vec(vec![kx as f64, ky as f64, kz as f64]));
                let k = k_vec.norm_l2();
                if k > gcutrho {
                    continue;
                }

                // \sum_I Z_I e^(i k_vec . R_I)
                let struct_fact = atom_positions
                    .rows()
                    .into_iter()
                    .zip(atomic_numbers)
                    .map(|(r_i, z_i)| *z_i as f64 * Complex::<f64>::new(0.0, k_vec.dot(&r_i)).exp())
                    .sum::<Complex<f64>>();

                e_long +=
                    (-k.powi(2) / (4.0 * sigma)).exp() * struct_fact.abs().powi(2) / k.powi(2);
            }
        }
    }
    e_long *= 4.0 * PI / 2.0 / cell_volume;

    let e_self = -atomic_numbers.map(|z| z.pow(2) as f64).sum() * (sigma / PI).sqrt();
    let e_charged = -PI / cell_volume / sigma * atomic_numbers.sum().pow(2) as f64 / 2.0;

    e_short + e_long + e_self + e_charged
}

// Implementation to calculate the forces on each atom due to the Ewald summation
// Analytical gradient was obteaind by deriving the Ewald energy with respect to the atomic positions R. R is compoused out of (x,y,z) coordinates of each atom.
// The final formula for the forces is composed out of two parts, a short-range part and a long-range part.
// The short-range part is calculated using the formula:  - Z_K * sum_N Z_N sum_T (R_K - R_N - T_vec) *(2sqrt(sigma)/sqrt(PI) * exp(-(|R_K-R_N-T|sqrt(sigma))^2) * |R_K-R_N-T| * erfc(|R_K-R_N-T|sqrt(sigma)) )/(|R_K-R_N-T|^3)
// The long range part is obtained with: - Z_K *4PI/V * sum_(G!=0) (G_vec/G^2) exp(-G^2/4sigma) * sum_N Z_N sin(G_vec.(R_K - R_N))
#[pyfunction]
#[allow(clippy::too_many_arguments)]
pub fn ewald_forces<'py>(
    py: Python<'py>,
    atom_positions_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
    atomic_numbers_np: np::PyReadonlyArray1<i64>, // shape (#atoms, 3)
    lattice_vectors_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
    lattice_vectors_reciprocal_np: np::PyReadonlyArray2<f64>, // shape (#atoms, 3)
    cell_volume: f64,
    gcutrho: f64,
    sigma: f64,
    // n_threads: usize,
) -> Bound<'py, np::PyArray2<f64>> {
    // if rayon::ThreadPoolBuilder::new()
    //     .num_threads(n_threads)
    //     .build_global()
    //     .is_err()
    // {};

    let atom_positions = atom_positions_np.as_array();
    let atomic_numbers = atomic_numbers_np.as_array();
    let lattice_vectors = lattice_vectors_np.as_array();
    let lattice_vectors_reciprocal = lattice_vectors_reciprocal_np.as_array();

    let alat = lattice_vectors.row(0).norm_l2();
    let t_vec_max_norm = 4.0 / sigma.sqrt() / alat;
    let b_norms = lattice_vectors_reciprocal
        .rows()
        .into_iter()
        .map(|row| row.norm_l2())
        .collect_vec();
    let (n_max_x, n_max_y, n_max_z) = b_norms
        .iter()
        .map(|b_norm| (b_norm * t_vec_max_norm) as i64 + 2)
        .collect_tuple()
        .unwrap();

    let t_vecs_unordered = (-n_max_x..=n_max_x)
        .cartesian_product(-n_max_y..=n_max_y)
        .cartesian_product(-n_max_z..=n_max_z)
        .map(|((nx, ny), nz)| {
            (
                lattice_vectors.dot(&Array1::from_vec(vec![nx as f64, ny as f64, nz as f64])),
                (nx, ny, nz),
            )
        });

    

    const EPS: f64 = 1e-8;

    let mut full_forces_ewald = ndarray::Array2::<f64>::zeros((atom_positions.nrows(), 3));
    
    for kth_atom in 0..atom_positions.nrows() {

        //let mut converged_real = false;
        let mut force_e_short = Array1::<f64>::zeros(3);
        let z_k: f64 = *atomic_numbers.get(kth_atom).unwrap() as f64;
        let pos_k = atom_positions.row(kth_atom);
        for (t_vec, (nx, ny, nz)) in t_vecs_unordered.clone()
        .sorted_by(|a, b| Ord::cmp(&OrderedFloat(a.0.norm_l2()), &OrderedFloat(b.0.norm_l2())))
        {
            for (n, pos_n) in atom_positions.rows().into_iter().enumerate() {
                let z_n = atomic_numbers.get(n).unwrap();
                let r_vec = pos_k.to_owned() - pos_n - &t_vec;
                let r = r_vec.norm_l2();
                if r < EPS || (t_vec.iter().all(|&x| x.abs() < EPS) && n == kth_atom) {
                    continue;
                }
                let erfc = special::Error::compl_error(r * sigma.sqrt());
                let exp_term = (-((r * sigma.sqrt()).powi(2))).exp();
                let coeff: f64= (2.0*sigma.sqrt())/PI.sqrt();
                let parameter = (*z_n as f64) * ((coeff * exp_term * r + erfc) / r.powi(3));
                let factor = r_vec * parameter;
                force_e_short += &factor;

            }
        }
        force_e_short *= -z_k;

        // Estimate size of Miller indices grid using the cutoff-energy and reciprocal lattice vectors
        // A simple, but not accurate enough, estimate would be gcutrho/|b_i| for i \in {1, 2, 3}
        // Here we take the shape of the reciprocal lattice into account:
        //       max[ gcutrho/(|b_i| + \sum_{j \neq i} b_i . b_j ) ] for i \in {1, 2, 3}
        let mut force_e_long = Array1::<f64>::zeros(3);
        let b1 = lattice_vectors_reciprocal.row(0);
        let b2 = lattice_vectors_reciprocal.row(1);
        let b3 = lattice_vectors_reciprocal.row(2);
        let k_max = [
            (gcutrho / (b1.norm_l2() + b1.dot(&b2) + b1.dot(&b3)))
                .abs()
                .round() as i64,
            (gcutrho / (b2.norm_l2() + b2.dot(&b1) + b2.dot(&b3)))
                .abs()
                .round() as i64,
            (gcutrho / (b3.norm_l2() + b3.dot(&b1) + b3.dot(&b2)))
                .abs()
                .round() as i64,
        ]
        .iter()
        .max()
        .unwrap()
        .to_owned();

        // let k_max = (gcutrho * 2.0).round() as i64;

        let mut force_e_long = Array1::<f64>::zeros(3);

        for kx in -k_max..=k_max {
            for ky in -k_max..=k_max {
                for kz in -k_max..=k_max {
                    if kx == 0 && ky == 0 && kz == 0 {
                        continue;
                    }
                    let k_vec = lattice_vectors_reciprocal
                        .t()
                        .dot(&Array1::from_vec(vec![kx as f64, ky as f64, kz as f64]));
                    let k: f64 = k_vec.norm_l2();
                    if k > gcutrho {
                        continue;
                    }

                    
                    let k2= k.powi(2);                     
                    let mut n_sum_coeff = 0.0;

                    for (n, pos_n) in atom_positions.rows().into_iter().enumerate() {
                        let z_n: f64 = *atomic_numbers.get(n).unwrap() as f64;
                        let dot_product = (pos_k.to_owned() - pos_n.to_owned()).dot(&k_vec);
                        let sin_coef = (dot_product).sin();
                        n_sum_coeff += z_n * sin_coef;
                    }

                    let exp_term: f64 = (-(1.0 / (4.0 * sigma)) * k2).exp();
                    let term = (&k_vec / k2) * exp_term * n_sum_coeff;
                    force_e_long += &term;
                }
            }
        }
        
        
        let prefactor = -z_k * ((4.0 * PI) / cell_volume);
        force_e_long *= prefactor;
        let total_force = force_e_short + force_e_long;
        // placing the total force inside an aray at the kth atom place
        full_forces_ewald.row_mut(kth_atom).assign(&total_force);
    } 
    full_forces_ewald.to_pyarray_bound(py)
}
