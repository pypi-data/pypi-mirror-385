use crate::error::Error;
use mysql_common::Value as MySqlValue;
use mysql_common::constants::ColumnType;
use mysql_common::packets::Column;
use pyo3::types::PyByteArray;
use pyo3::{
    IntoPyObjectExt,
    prelude::*,
    sync::PyOnceLock,
    types::{PyBytes, PyString},
};

static DATETIME_CLASS: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static DATE_CLASS: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static TIMEDELTA_CLASS: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static DECIMAL_CLASS: PyOnceLock<Py<PyAny>> = PyOnceLock::new();
static JSON_MODULE: PyOnceLock<Py<PyModule>> = PyOnceLock::new();

fn get_datetime_class<'py>(py: Python<'py>) -> PyResult<&'py Bound<'py, PyAny>> {
    Ok(DATETIME_CLASS
        .get_or_init(py, || {
            PyModule::import(py, "datetime")
                .unwrap()
                .getattr("datetime")
                .unwrap()
                .unbind()
        })
        .bind(py))
}

fn get_date_class<'py>(py: Python<'py>) -> PyResult<&'py Bound<'py, PyAny>> {
    Ok(DATE_CLASS
        .get_or_init(py, || {
            PyModule::import(py, "datetime")
                .unwrap()
                .getattr("date")
                .unwrap()
                .unbind()
        })
        .bind(py))
}

fn get_timedelta_class<'py>(py: Python<'py>) -> PyResult<&'py Bound<'py, PyAny>> {
    Ok(TIMEDELTA_CLASS
        .get_or_init(py, || {
            PyModule::import(py, "datetime")
                .unwrap()
                .getattr("timedelta")
                .unwrap()
                .unbind()
        })
        .bind(py))
}

fn get_decimal_class<'py>(py: Python<'py>) -> PyResult<&'py Bound<'py, PyAny>> {
    Ok(DECIMAL_CLASS
        .get_or_init(py, || {
            PyModule::import(py, "decimal")
                .unwrap()
                .getattr("Decimal")
                .unwrap()
                .unbind()
        })
        .bind(py))
}

fn get_json_module<'py>(py: Python<'py>) -> PyResult<&'py Bound<'py, PyModule>> {
    Ok(JSON_MODULE
        .get_or_init(py, || PyModule::import(py, "json").unwrap().unbind())
        .bind(py))
}

#[derive(Clone)]
pub struct Value {
    pub inner: MySqlValue,
}

impl FromPyObject<'_, '_> for Value {
    type Error = PyErr;

    fn extract(ob: Borrowed<PyAny>) -> Result<Self, Self::Error> {
        let py = ob.py();

        // Get the type object and its name
        let type_obj = ob.get_type();
        let type_name = type_obj.name()?; // TODO: use qualname() with 'builtins.int' for precise ident

        // Match on type name
        let inner = match type_name.to_str()? {
            "NoneType" => MySqlValue::NULL,
            "bool" => {
                let v = ob.extract::<bool>()?;
                MySqlValue::Int(v as i64)
            }
            "int" => {
                // Try to fit in i64 first, then u64, otherwise convert to string
                if let Ok(v) = ob.extract::<i64>() {
                    MySqlValue::Int(v)
                } else if let Ok(v) = ob.extract::<u64>() {
                    MySqlValue::UInt(v)
                } else {
                    // Integer too large for i64/u64, store as string
                    let int_str = ob.str()?.to_str()?.as_bytes().to_vec();
                    MySqlValue::Bytes(int_str)
                }
            }
            "float" => {
                let v = ob.extract::<f64>()?;
                MySqlValue::Double(v)
            }
            "str" => {
                let v = ob.extract::<String>()?;
                MySqlValue::Bytes(v.into_bytes())
            }
            "bytes" => {
                let v = ob.extract::<&[u8]>()?;
                MySqlValue::Bytes(v.to_vec())
            }
            "bytearray" => {
                let v = ob.downcast::<PyByteArray>()?;
                MySqlValue::Bytes(v.to_vec())
            }
            "tuple" | "list" | "set" | "frozenset" | "dict" => {
                // Serialize collections to JSON
                let json_module = get_json_module(py)?;
                let json_str = json_module
                    .call_method1("dumps", (ob,))?
                    .extract::<String>()?;
                MySqlValue::Bytes(json_str.into_bytes())
            }
            "datetime" => {
                // datetime.datetime
                let year = ob.getattr("year")?.extract::<u16>()?;
                let month = ob.getattr("month")?.extract::<u8>()?;
                let day = ob.getattr("day")?.extract::<u8>()?;
                let hour = ob.getattr("hour")?.extract::<u8>()?;
                let minute = ob.getattr("minute")?.extract::<u8>()?;
                let second = ob.getattr("second")?.extract::<u8>()?;
                let microsecond = ob.getattr("microsecond")?.extract::<u32>()?;
                MySqlValue::Date(year, month, day, hour, minute, second, microsecond)
            }
            "date" => {
                // datetime.date
                let year = ob.getattr("year")?.extract::<u16>()?;
                let month = ob.getattr("month")?.extract::<u8>()?;
                let day = ob.getattr("day")?.extract::<u8>()?;
                MySqlValue::Date(year, month, day, 0, 0, 0, 0)
            }
            "time" => {
                // datetime.time
                let hour = ob.getattr("hour")?.extract::<u8>()?;
                let minute = ob.getattr("minute")?.extract::<u8>()?;
                let second = ob.getattr("second")?.extract::<u8>()?;
                let microsecond = ob.getattr("microsecond")?.extract::<u32>()?;
                MySqlValue::Time(false, 0, hour, minute, second, microsecond)
            }
            "timedelta" => {
                // datetime.timedelta
                let total_seconds = ob.call_method0("total_seconds")?.extract::<f64>()?;
                let is_negative = total_seconds < 0.0;
                let abs_seconds = total_seconds.abs();

                let days = (abs_seconds / 86400.0) as u32;
                let remaining = abs_seconds % 86400.0;
                let hours = (remaining / 3600.0) as u8;
                let remaining = remaining % 3600.0;
                let minutes = (remaining / 60.0) as u8;
                let seconds = (remaining % 60.0) as u8;
                let microseconds = ((remaining % 1.0) * 1_000_000.0) as u32;

                MySqlValue::Time(is_negative, days, hours, minutes, seconds, microseconds)
            }
            "struct_time" => {
                // time.struct_time
                let year = ob.getattr("tm_year")?.extract::<u16>()?;
                let month = ob.getattr("tm_mon")?.extract::<u8>()?;
                let day = ob.getattr("tm_mday")?.extract::<u8>()?;
                let hour = ob.getattr("tm_hour")?.extract::<u8>()?;
                let minute = ob.getattr("tm_min")?.extract::<u8>()?;
                let second = ob.getattr("tm_sec")?.extract::<u8>()?;
                MySqlValue::Date(year, month, day, hour, minute, second, 0)
            }
            "Decimal" => {
                // decimal.Decimal
                let decimal_str = ob.str()?.to_str()?.as_bytes().to_vec();
                MySqlValue::Bytes(decimal_str)
            }
            // uuid.UUID
            "UUID" => {
                let hex = ob.getattr("hex")?.extract::<String>()?;
                MySqlValue::Bytes(hex.into_bytes())
            }
            _ => {
                return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
                    "Unsupported value type: {:?}",
                    type_obj.fully_qualified_name()
                )));
            }
        };

        Ok(Value { inner })
    }
}

/// `value` is copied to the Python heap
pub fn value_to_python<'py>(
    py: Python<'py>,
    value: &MySqlValue,
    column: &Column,
) -> PyResult<Bound<'py, PyAny>> {
    // Handle NULL first as it's independent of column type
    if matches!(value, MySqlValue::NULL) {
        return Ok(py.None().into_bound(py));
    }

    let col_type = column.column_type();

    let bound = match col_type {
        // Date type
        ColumnType::MYSQL_TYPE_DATE => {
            match value {
                MySqlValue::Date(year, month, day, _, _, _, _) => {
                    get_date_class(py)?.call1((year, month, day))?
                }
                MySqlValue::Bytes(b) => {
                    let date_str =
                        std::str::from_utf8(b).map_err(|_| Error::decode_error(col_type, b))?;

                    // Parse MySQL date format: YYYY-MM-DD
                    let parts: Vec<&str> = date_str.split('-').collect();
                    if parts.len() != 3 {
                        return Err(Error::decode_error(col_type, b).into());
                    }

                    let year = parts[0]
                        .parse::<u16>()
                        .map_err(|_| Error::decode_error(col_type, b))?;
                    let month = parts[1]
                        .parse::<u8>()
                        .map_err(|_| Error::decode_error(col_type, b))?;
                    let day = parts[2]
                        .parse::<u8>()
                        .map_err(|_| Error::decode_error(col_type, b))?;

                    get_date_class(py)?.call1((year, month, day))?
                }
                _ => {
                    return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
                        "Unexpected value type for DATE column: {:?}",
                        value
                    )));
                }
            }
        }

        // Time type
        ColumnType::MYSQL_TYPE_TIME => {
            match value {
                MySqlValue::Time(is_negative, days, hours, minutes, seconds, microseconds) => {
                    let timedelta = get_timedelta_class(py)?.call1((
                        days,
                        seconds,
                        microseconds,
                        0,
                        minutes,
                        hours,
                    ))?;
                    if *is_negative {
                        timedelta.call_method0("__neg__")?
                    } else {
                        timedelta
                    }
                }
                MySqlValue::Bytes(b) => {
                    let time_str =
                        std::str::from_utf8(b).map_err(|_| Error::decode_error(col_type, b))?;

                    // Parse MySQL time format: HH:MM:SS or HH:MM:SS.ffffff
                    // Can also be negative and exceed 24 hours for TIME type
                    let (is_negative, time_part) =
                        if let Some(time_str) = time_str.strip_prefix('-') {
                            (true, time_str)
                        } else {
                            (false, time_str)
                        };

                    let parts: Vec<&str> = time_part.split(':').collect();
                    if parts.len() != 3 {
                        return Err(Error::decode_error(col_type, b).into());
                    }

                    let hour = parts[0]
                        .parse::<u32>()
                        .map_err(|_| Error::decode_error(col_type, b))?;
                    let minute = parts[1]
                        .parse::<u8>()
                        .map_err(|_| Error::decode_error(col_type, b))?;

                    let (second, microsecond) = if let Some((sec_str, micro_str)) =
                        parts[2].split_once('.')
                    {
                        let second = sec_str
                            .parse::<u8>()
                            .map_err(|_| Error::decode_error(col_type, b))?;
                        let micro_padded = format!("{:0<6}", &micro_str[..micro_str.len().min(6)]);
                        let microsecond = micro_padded
                            .parse::<u32>()
                            .map_err(|_| Error::decode_error(col_type, b))?;
                        (second, microsecond)
                    } else {
                        let second = parts[2]
                            .parse::<u8>()
                            .map_err(|_| Error::decode_error(col_type, b))?;
                        (second, 0)
                    };

                    // MySQL TIME can exceed 24 hours, so use timedelta
                    let total_seconds = hour * 3600 + minute as u32 * 60 + second as u32;
                    let days = total_seconds / 86400;
                    let remaining_seconds = total_seconds % 86400;

                    let timedelta =
                        get_timedelta_class(py)?.call1((days, remaining_seconds, microsecond))?;
                    if is_negative {
                        timedelta.call_method0("__neg__")?
                    } else {
                        timedelta
                    }
                }
                _ => {
                    return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
                        "Unexpected value type for TIME column: {:?}",
                        value
                    )));
                }
            }
        }

        // DateTime and Timestamp types
        ColumnType::MYSQL_TYPE_DATETIME | ColumnType::MYSQL_TYPE_TIMESTAMP => {
            match value {
                MySqlValue::Date(year, month, day, hour, minutes, seconds, microseconds) => {
                    get_datetime_class(py)?.call1((
                        year,
                        month,
                        day,
                        hour,
                        minutes,
                        seconds,
                        microseconds,
                    ))?
                }
                MySqlValue::Bytes(b) => {
                    let datetime_str =
                        std::str::from_utf8(b).map_err(|_| Error::decode_error(col_type, b))?;

                    // Parse MySQL datetime format: YYYY-MM-DD HH:MM:SS or YYYY-MM-DD HH:MM:SS.ffffff
                    let parts: Vec<&str> = datetime_str.split(' ').collect();
                    if parts.len() != 2 {
                        return Err(Error::decode_error(col_type, b).into());
                    }

                    let date_parts: Vec<&str> = parts[0].split('-').collect();
                    if date_parts.len() != 3 {
                        return Err(Error::decode_error(col_type, b).into());
                    }

                    let time_parts: Vec<&str> = parts[1].split(':').collect();
                    if time_parts.len() != 3 {
                        return Err(Error::decode_error(col_type, b).into());
                    }

                    let year = date_parts[0]
                        .parse::<u16>()
                        .map_err(|_| Error::decode_error(col_type, b))?;
                    let month = date_parts[1]
                        .parse::<u8>()
                        .map_err(|_| Error::decode_error(col_type, b))?;
                    let day = date_parts[2]
                        .parse::<u8>()
                        .map_err(|_| Error::decode_error(col_type, b))?;
                    let hour = time_parts[0]
                        .parse::<u8>()
                        .map_err(|_| Error::decode_error(col_type, b))?;
                    let minute = time_parts[1]
                        .parse::<u8>()
                        .map_err(|_| Error::decode_error(col_type, b))?;

                    let (second, microsecond) = if let Some((sec_str, micro_str)) =
                        time_parts[2].split_once('.')
                    {
                        let second = sec_str
                            .parse::<u8>()
                            .map_err(|_| Error::decode_error(col_type, b))?;
                        let micro_padded = format!("{:0<6}", &micro_str[..micro_str.len().min(6)]);
                        let microsecond = micro_padded
                            .parse::<u32>()
                            .map_err(|_| Error::decode_error(col_type, b))?;
                        (second, microsecond)
                    } else {
                        let second = time_parts[2]
                            .parse::<u8>()
                            .map_err(|_| Error::decode_error(col_type, b))?;
                        (second, 0)
                    };

                    get_datetime_class(py)?.call1((
                        year,
                        month,
                        day,
                        hour,
                        minute,
                        second,
                        microsecond,
                    ))?
                }
                _ => {
                    return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
                        "Unexpected value type for DATETIME/TIMESTAMP column: {:?}",
                        value
                    )));
                }
            }
        }

        // Integer types
        ColumnType::MYSQL_TYPE_LONGLONG
        | ColumnType::MYSQL_TYPE_LONG
        | ColumnType::MYSQL_TYPE_INT24
        | ColumnType::MYSQL_TYPE_SHORT
        | ColumnType::MYSQL_TYPE_TINY
        | ColumnType::MYSQL_TYPE_YEAR => {
            match value {
                MySqlValue::Int(i) => i.into_bound_py_any(py)?,
                MySqlValue::UInt(u) => u.into_bound_py_any(py)?,
                MySqlValue::Bytes(b) => {
                    match std::str::from_utf8(b) {
                        Ok(int_str) => {
                            // Use PyLong::from_str to handle arbitrarily large integers
                            match py.import("builtins")?.getattr("int")?.call1((int_str,)) {
                                Ok(py_int) => py_int,
                                Err(_) => PyBytes::new(py, b).into_any(),
                            }
                        }
                        Err(_) => PyBytes::new(py, b).into_any(),
                    }
                }
                _ => {
                    return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
                        "Unexpected value type for integer column: {:?}",
                        value
                    )));
                }
            }
        }

        // Floating point types
        ColumnType::MYSQL_TYPE_FLOAT | ColumnType::MYSQL_TYPE_DOUBLE => {
            match value {
                MySqlValue::Float(f) => {
                    let mut buffer = ryu::Buffer::new();
                    buffer
                        .format(*f)
                        .parse::<f64>()
                        .unwrap() // unwrap(): f32 -> str -> f64 never fails
                        .into_bound_py_any(py)?
                }
                MySqlValue::Double(f) => f.into_bound_py_any(py)?,
                MySqlValue::Bytes(b) => match std::str::from_utf8(b) {
                    Ok(float_str) => match float_str.parse::<f64>() {
                        Ok(f) => f.into_bound_py_any(py)?,
                        Err(_) => PyBytes::new(py, b).into_any(),
                    },
                    Err(_) => PyBytes::new(py, b).into_any(),
                },
                _ => {
                    return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
                        "Unexpected value type for float column: {:?}",
                        value
                    )));
                }
            }
        }

        // JSON type
        ColumnType::MYSQL_TYPE_JSON => match value {
            MySqlValue::Bytes(b) => match PyString::from_bytes(py, b) {
                Ok(json_str) => {
                    let json_module = get_json_module(py)?;
                    json_module.call_method1("loads", (json_str,))?
                }
                Err(_) => PyBytes::new(py, b).into_any(),
            },
            _ => {
                return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
                    "Unexpected value type for JSON column: {:?}",
                    value
                )));
            }
        },

        // Decimal types
        ColumnType::MYSQL_TYPE_DECIMAL | ColumnType::MYSQL_TYPE_NEWDECIMAL => match value {
            MySqlValue::Bytes(b) => match PyString::from_bytes(py, b) {
                Ok(decimal_str) => get_decimal_class(py)?.call1((decimal_str,))?,
                Err(_) => PyBytes::new(py, b).into_any(),
            },
            _ => {
                return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
                    "Unexpected value type for DECIMAL column: {:?}",
                    value
                )));
            }
        },

        // Text and string types
        ColumnType::MYSQL_TYPE_VARCHAR
        | ColumnType::MYSQL_TYPE_VAR_STRING
        | ColumnType::MYSQL_TYPE_STRING
        | ColumnType::MYSQL_TYPE_TINY_BLOB
        | ColumnType::MYSQL_TYPE_MEDIUM_BLOB
        | ColumnType::MYSQL_TYPE_LONG_BLOB
        | ColumnType::MYSQL_TYPE_BLOB => {
            match value {
                MySqlValue::Bytes(b) => {
                    if column.character_set() == 63 {
                        PyBytes::new(py, b).into_any()
                    } else {
                        // TODO: this can be non-utf8 if character_set_results is not utf8*
                        match PyString::from_bytes(py, b) {
                            Ok(s) => s.into_any(),
                            Err(_) => PyBytes::new(py, b).into_any(),
                        }
                    }
                }
                _ => {
                    return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
                        "Unexpected value type for text column: {:?}",
                        value
                    )));
                }
            }
        }

        // ENUM and SET types
        ColumnType::MYSQL_TYPE_ENUM | ColumnType::MYSQL_TYPE_SET => match value {
            MySqlValue::Bytes(b) => match PyString::from_bytes(py, b) {
                Ok(s) => s.into_any(),
                Err(_) => PyBytes::new(py, b).into_any(),
            },
            _ => {
                return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
                    "Unexpected value type for ENUM/SET column: {:?}",
                    value
                )));
            }
        },

        // BIT type
        ColumnType::MYSQL_TYPE_BIT => match value {
            MySqlValue::Bytes(b) => PyBytes::new(py, b).into_any(),
            _ => {
                return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
                    "Unexpected value type for BIT column: {:?}",
                    value
                )));
            }
        },

        // GEOMETRY type
        ColumnType::MYSQL_TYPE_GEOMETRY => match value {
            MySqlValue::Bytes(b) => PyBytes::new(py, b).into_any(),
            _ => {
                return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(format!(
                    "Unexpected value type for GEOMETRY column: {:?}",
                    value
                )));
            }
        },

        // Default: handle any unimplemented types
        _ => {
            log::error!("Unimplemented column type: {:?}", col_type);
            match value {
                MySqlValue::Int(i) => i.into_bound_py_any(py)?,
                MySqlValue::UInt(u) => u.into_bound_py_any(py)?,
                MySqlValue::Float(f) => {
                    let mut buffer = ryu::Buffer::new();
                    buffer
                        .format(*f)
                        .parse::<f64>()
                        .unwrap()
                        .into_bound_py_any(py)?
                }
                MySqlValue::Double(f) => f.into_bound_py_any(py)?,
                MySqlValue::Date(year, month, day, hour, minutes, seconds, microseconds) => {
                    get_datetime_class(py)?.call1((
                        year,
                        month,
                        day,
                        hour,
                        minutes,
                        seconds,
                        microseconds,
                    ))?
                }
                MySqlValue::Time(is_negative, days, hours, minutes, seconds, microseconds) => {
                    let timedelta = get_timedelta_class(py)?.call1((
                        days,
                        seconds,
                        microseconds,
                        0,
                        minutes,
                        hours,
                    ))?;
                    if *is_negative {
                        timedelta.call_method0("__neg__")?
                    } else {
                        timedelta
                    }
                }
                MySqlValue::Bytes(b) => match PyString::from_bytes(py, b) {
                    Ok(s) => s.into_any(),
                    Err(_) => PyBytes::new(py, b).into_any(),
                },
                MySqlValue::NULL => unreachable!(), // Already handled at the beginning
            }
        }
    };

    Ok(bound)
}

impl From<Value> for MySqlValue {
    fn from(value: Value) -> Self {
        value.inner
    }
}

impl From<MySqlValue> for Value {
    fn from(value: MySqlValue) -> Self {
        Value { inner: value }
    }
}
