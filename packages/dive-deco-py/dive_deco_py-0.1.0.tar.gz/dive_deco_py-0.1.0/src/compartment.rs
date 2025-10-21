use pyo3::prelude::*;
use dive_deco::Compartment as CompartmentRs;

#[pyclass]
#[derive(Clone)]
pub struct Compartment {
    compartment_rs: CompartmentRs
}

#[pymethods]
impl Compartment {
    #[getter]
    pub fn no(&self) -> u8 {
        self.compartment_rs.no
    }
    
    #[getter]
    pub fn he_ip(&self) -> f64 {
        self.compartment_rs.he_ip
    }
    
    #[getter]
    pub fn n2_ip(&self) -> f64 {
        self.compartment_rs.n2_ip
    }
    
    #[getter]
    pub fn total_ip(&self) -> f64 {
        self.compartment_rs.total_ip
    }
    
    #[getter]
    pub fn m_value_raw(&self) -> f64 {
        self.compartment_rs.m_value_raw
    }
    
    #[getter]
    pub fn m_value_calc(&self) -> f64 {
        self.compartment_rs.m_value_calc
    }
    
    #[getter]
    pub fn min_tolerable_amb_pressure(&self) -> f64 {
        self.compartment_rs.min_tolerable_amb_pressure
    }
}

impl From<CompartmentRs> for Compartment {
    fn from(compartment_rs: CompartmentRs) -> Self {
        Self { compartment_rs }
    }
}
