use pyo3::prelude::*;
use dive_deco::Gas as GasRs;

#[pyclass]
#[derive(Clone)]
pub struct Gas {
    pub gas_rs: GasRs
}

#[pymethods]
impl Gas {
    #[new]
    pub fn new(o2: f64, he: f64) -> Self {
        Self {
            gas_rs: GasRs::new(o2, he)
        }
    }

    #[staticmethod]
    pub fn air() -> Self {
        Self {
            gas_rs: GasRs::air()
        }
    }
}