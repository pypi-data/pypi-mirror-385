use pyo3::{IntoPyObjectExt, prelude::*, types::PyDate};

#[inline]
pub(super) fn parse_int_arg(py: Python, arg: &str) -> PyResult<Py<PyAny>> {
    let ret = arg.parse::<i32>()?;
    ret.into_py_any(py)
}

#[inline]
pub(super) fn parse_float_arg(py: Python, arg: &str) -> PyResult<Py<PyAny>> {
    let ret = arg.parse::<f32>()?;
    ret.into_py_any(py)
}

#[inline]
pub(super) fn parse_date_arg(py: Python, arg: &str) -> PyResult<Py<PyAny>> {
    let year = &arg[0..4].parse::<i32>()?;
    let month = &arg[5..7].parse::<u8>()?;
    let day = &arg[8..10].parse::<u8>()?;
    let date = PyDate::new(py, *year, *month, *day)?;
    date.into_py_any(py)
}
