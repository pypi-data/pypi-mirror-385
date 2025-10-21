mod buhlmann_model;
mod gas;
mod deco;
mod compartment;

use pyo3::prelude::*;
use buhlmann_model::BuhlmannModel;
use gas::Gas;
use compartment::Compartment;


/// A Python module implemented in Rust.
#[pymodule]
fn dive_deco_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<BuhlmannModel>()?;
    m.add_class::<Gas>()?;
    m.add_class::<Compartment>()?;
    Ok(())
}
