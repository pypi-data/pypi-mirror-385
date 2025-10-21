pub mod fodot;
mod interior_mut;
pub mod solver;

mod python_module {
    use super::*;
    use pyo3::prelude::*;

    #[pymodule]
    fn sli_lib(m: &Bound<'_, PyModule>) -> PyResult<()> {
        let fodot = fodot::submodule(m.py())?;
        m.gil_used(false)?;
        m.add_submodule(&fodot)?;
        m.py()
            .import("sys")?
            .getattr("modules")?
            .set_item("sli_lib._fodot", &fodot)?;
        let solver = solver::submodule(m.py())?;
        m.add_submodule(&solver)?;
        m.py()
            .import("sys")?
            .getattr("modules")?
            .set_item("sli_lib._solver", &solver)?;
        Ok(())
    }
}
