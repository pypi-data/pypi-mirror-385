use std::path::PathBuf;

use pyo3::{pyclass, pymethods};

/// Specifies the intent for a (TLS) keylogger to be used in a client or server configuration.
///
/// This type allows you to control how TLS session keys are logged for debugging or analysis.
/// You can either use the default environment variable (`SSLKEYLOGFILE`) or specify a file path
/// directly. This is useful for tools like Wireshark that can decrypt TLS traffic if provided
/// with the correct session keys.
#[derive(Clone)]
#[pyclass]
pub struct KeyLog(pub wreq::tls::KeyLog);

#[pymethods]
impl KeyLog {
    /// Use the environment variable SSLKEYLOGFILE.
    #[staticmethod]
    pub fn environment() -> Self {
        KeyLog(wreq::tls::KeyLog::from_env())
    }

    /// Log keys to the specified file path.
    #[staticmethod]
    pub fn file(path: PathBuf) -> Self {
        KeyLog(wreq::tls::KeyLog::from_file(path))
    }
}
