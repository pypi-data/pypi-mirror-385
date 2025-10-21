// This file was generated. DO NOT EDIT.
mod part_00;
mod part_01;
mod part_02;
mod part_03;
mod part_04;
mod part_05;
mod part_06;
mod part_07;
mod part_08;
mod part_09;
mod part_10;
mod part_11;
mod part_12;
mod part_13;
mod part_14;
mod part_15;
mod part_16;
use crate::{Icon, finder::get_icon};
use pyo3::prelude::*;

#[pymodule]
pub fn simple_icons_pack(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_icon, m)?)?;
    m.add_class::<Icon>()?;
    part_00::bind_part_0(m)?;
    part_01::bind_part_1(m)?;
    part_02::bind_part_2(m)?;
    part_03::bind_part_3(m)?;
    part_04::bind_part_4(m)?;
    part_05::bind_part_5(m)?;
    part_06::bind_part_6(m)?;
    part_07::bind_part_7(m)?;
    part_08::bind_part_8(m)?;
    part_09::bind_part_9(m)?;
    part_10::bind_part_10(m)?;
    part_11::bind_part_11(m)?;
    part_12::bind_part_12(m)?;
    part_13::bind_part_13(m)?;
    part_14::bind_part_14(m)?;
    part_15::bind_part_15(m)?;
    part_16::bind_part_16(m)?;
    Ok(())
}
