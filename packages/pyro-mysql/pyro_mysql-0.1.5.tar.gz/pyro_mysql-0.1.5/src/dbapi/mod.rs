pub mod async_conn;
pub mod async_cursor;
pub mod conn;
pub mod cursor;
pub mod error;
pub mod type_constructor;
pub mod type_object;

use std::sync::Arc;

use crate::{
    r#async::opts::AsyncOpts,
    dbapi::{async_conn::AsyncDbApiConn, conn::DbApiConn, error::DbApiResult},
    error::Error,
    params::Params,
    sync::opts::SyncOpts,
    util::{PyroFuture, rust_future_into_py, url_error_to_pyerr},
};
use either::Either;

use mysql_async::prelude::Queryable;
use pyo3::prelude::*;

#[pyfunction]
#[pyo3(signature = (url_or_opts, autocommit=Some(false)))]
pub fn connect(
    url_or_opts: Either<String, PyRef<SyncOpts>>,
    autocommit: Option<bool>,
) -> DbApiResult<DbApiConn> {
    let conn = DbApiConn::new(url_or_opts)?;
    if let Some(on) = autocommit {
        conn.set_autocommit(on)?;
    }
    Ok(conn)
}

#[pyfunction()]
#[pyo3(name = "connect", signature = (url_or_opts, autocommit=Some(false)))]
pub fn connect_async(
    py: Python,
    url_or_opts: Either<String, PyRef<AsyncOpts>>,
    autocommit: Option<bool>,
) -> DbApiResult<Py<PyroFuture>> {
    let opts = match url_or_opts {
        Either::Left(url) => mysql_async::Opts::from_url(&url).map_err(url_error_to_pyerr)?,
        Either::Right(opts) => opts.opts.clone(),
    };
    Ok(rust_future_into_py(py, async move {
        let mut conn = mysql_async::Conn::new(opts).await?;
        if let Some(on) = autocommit {
            let query = if on {
                "SET autocommit=1"
            } else {
                "SET autocommit=0"
            };
            conn.exec_drop(query, Params::default())
                .await
                .map_err(Error::from)?;
        }
        Ok(AsyncDbApiConn(Arc::new(tokio::sync::RwLock::new(Some(
            conn,
        )))))
    })?)
}
