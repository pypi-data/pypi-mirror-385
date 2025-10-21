use pyo3::prelude::*;

use crate::error::{Error, PyroResult};

#[pyclass(module = "pyro_mysql.sync", name = "PoolOpts")]
#[derive(Clone, Debug)]
pub struct SyncPoolOpts {
    pub(crate) inner: mysql::PoolOpts,
}

#[pymethods]
impl SyncPoolOpts {
    #[new]
    pub fn new() -> Self {
        Self {
            inner: mysql::PoolOpts::default(),
        }
    }

    pub fn with_constraints(&self, constraints: (usize, usize)) -> PyroResult<Self> {
        let (min, max) = constraints;
        match mysql::PoolConstraints::new(min, max) {
            Some(pool_constraints) => Ok(Self {
                inner: self.inner.clone().with_constraints(pool_constraints),
            }),
            None => Err(Error::IncorrectApiUsageError(
                "Invalid pool constraints: min must be <= max",
            )),
        }
    }
}

impl Default for SyncPoolOpts {
    fn default() -> Self {
        Self::new()
    }
}
