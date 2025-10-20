use pyo3::prelude::*;

mod calc_ewald;
mod calc_pp;

/// A Python module implemented in Rust.
#[pymodule]
fn dopyqo_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(calc_pp::v_loc_pw_unique, m)?)?;
    m.add_function(wrap_pyfunction!(calc_pp::calc_g_zero_lim, m)?)?;
    m.add_function(wrap_pyfunction!(calc_pp::calc_prefactor_mat, m)?)?;
    m.add_function(wrap_pyfunction!(calc_pp::v_nl_pw, m)?)?;
    m.add_function(wrap_pyfunction!(calc_pp::v_loc_row_by_row, m)?)?;
    m.add_function(wrap_pyfunction!(calc_pp::v_loc_diag_row_by_row, m)?)?;
    m.add_function(wrap_pyfunction!(calc_pp::v_loc_on_grid, m)?)?;
    m.add_function(wrap_pyfunction!(calc_pp::v_nl_row_by_row, m)?)?;
    m.add_function(wrap_pyfunction!(calc_pp::v_nl_row_by_row_par, m)?)?;
    m.add_function(wrap_pyfunction!(calc_ewald::ewald, m)?)?;
    m.add_function(wrap_pyfunction!(calc_ewald::ewald_forces, m)?)?;
    Ok(())
}
