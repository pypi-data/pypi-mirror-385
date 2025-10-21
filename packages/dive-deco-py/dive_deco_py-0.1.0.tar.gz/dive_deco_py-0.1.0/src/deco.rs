use pyo3::prelude::*;

#[pyclass]
pub struct Deco {
    #[pyo3(get)]
    pub tts: f64,
    #[pyo3(get)]
    pub tts_at_5: f64,
    #[pyo3(get)]
    pub tts_delta_at_5: f64

}