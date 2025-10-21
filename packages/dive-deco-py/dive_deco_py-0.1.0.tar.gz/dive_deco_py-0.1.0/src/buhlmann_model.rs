use pyo3::{pyclass, pymethods, PyRef, PyRefMut};
use dive_deco::{BuhlmannConfig as BuhlmannConfigRs, BuhlmannModel as BuhlmannModelRs, DecoModel as DecoModelRs, Depth as DepthRs, Gas as GasRs, Time as TimeRs};
use dive_deco::CeilingType::Adaptive;
use crate::deco::Deco;
use crate::gas::Gas;
use crate::compartment::Compartment;

#[pyclass]
pub struct BuhlmannModel {
    model_rs: BuhlmannModelRs,
}

#[pyclass]
pub struct Supersaturation {
    #[pyo3(get)]
    gf_99: f64,
    #[pyo3(get)]
    gf_surf: f64,
}

#[pymethods]
impl BuhlmannModel {
    #[new]
    pub fn new() -> Self {
        let config = BuhlmannConfigRs::default().with_gradient_factors(30, 70).with_ceiling_type(Adaptive);
        BuhlmannModel {
            model_rs: BuhlmannModelRs::new(config),
        }
    }

    fn record(mut self_: PyRefMut<'_, Self>, depth: f64, time: f64, gas: Gas) -> () {
        self_.model_rs.record(
            DepthRs::from_meters(depth),
            TimeRs::from_minutes(time),
            &gas.gas_rs
        )
    }

    fn record_travel_with_rate(mut self_: PyRefMut<'_, Self>, depth: f64, rate: f64, gas: Gas) -> () {
        self_.model_rs.record_travel_with_rate(
            DepthRs::from_meters(depth),
            rate,
            &gas.gas_rs
        )
    }

    fn ndl(self_: PyRef<'_, Self>) -> f64 {
        self_.model_rs.ndl().as_minutes()
    }

    fn deco(self_: PyRef<'_, Self>, gas_mixes: Vec<Gas>) -> Deco {
        let gasses_rs: Vec<GasRs> = gas_mixes.iter().map(|g| g.gas_rs).collect();
        let deco = self_.model_rs.deco(gasses_rs).unwrap();

        Deco {
            tts: deco.tts.as_minutes(),
            tts_at_5: deco.tts_at_5.as_minutes(),
            tts_delta_at_5: deco.tts_delta_at_5.as_minutes()
        }
    }

    fn ceiling(self_: PyRef<'_, Self>) -> f64 {
        self_.model_rs.ceiling().as_meters()
    }

    fn supersaturation(self_: PyRef<'_, Self>) -> Supersaturation {
        let supersaturation_rs = self_.model_rs.supersaturation();
        Supersaturation {
            gf_99: supersaturation_rs.gf_99,
            gf_surf: supersaturation_rs.gf_surf,
        }
    }

    fn tissues(self_: PyRef<'_, Self>) -> Vec<Compartment> {
        self_.model_rs.tissues()
            .into_iter()
            .map(|c| c.into())
            .collect()
    }
}
