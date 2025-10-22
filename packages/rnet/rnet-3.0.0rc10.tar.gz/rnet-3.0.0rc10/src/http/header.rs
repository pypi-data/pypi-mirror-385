use std::fmt;

use bytes::Bytes;
use pyo3::{
    prelude::*,
    pybacked::{PyBackedBytes, PyBackedStr},
    types::{PyDict, PyIterator, PyList},
};
use wreq::header::{self, HeaderName, HeaderValue};

use crate::buffer::PyBuffer;

/// A HTTP header map.
#[pyclass(subclass, str)]
#[derive(Clone)]
pub struct HeaderMap(pub header::HeaderMap);

/// A HTTP original header map.
#[pyclass(subclass, str)]
#[derive(Clone)]
pub struct OrigHeaderMap(pub header::OrigHeaderMap);

// ===== impl HeaderMap =====

#[pymethods]
impl HeaderMap {
    /// Creates a new `HeaderMap` from an optional dictionary.
    #[new]
    #[pyo3(signature = (dict=None, capacity=None))]
    fn new(dict: Option<&Bound<'_, PyDict>>, capacity: Option<usize>) -> HeaderMap {
        let mut headers = capacity
            .map(header::HeaderMap::with_capacity)
            .unwrap_or_default();

        // This section of memory might be retained by the Rust object,
        // and we want to prevent Python's garbage collector from managing it.
        if let Some(dict) = dict {
            for (name, value) in dict.iter() {
                let name = match name
                    .extract::<PyBackedStr>()
                    .map(|n| HeaderName::from_bytes(n.as_bytes()))
                {
                    Ok(Ok(n)) => n,
                    _ => continue,
                };

                let value = match value
                    .extract::<PyBackedStr>()
                    .map(Bytes::from_owner)
                    .map(HeaderValue::from_maybe_shared)
                {
                    Ok(Ok(v)) => v,
                    _ => continue,
                };

                headers.insert(name, value);
            }
        }

        HeaderMap(headers)
    }

    /// Returns a reference to the value associated with the key.
    ///
    /// If there are multiple values associated with the key, then the first one
    /// is returned. Use `get_all` to get all values associated with a given
    /// key. Returns `None` if there are no values associated with the key.
    #[pyo3(signature = (key, default=None))]
    fn get<'py>(
        &self,
        py: Python<'py>,
        key: PyBackedStr,
        default: Option<PyBackedBytes>,
    ) -> Option<PyBuffer> {
        py.detach(|| {
            self.0.get::<&str>(key.as_ref()).cloned().or_else(|| {
                match default
                    .map(Bytes::from_owner)
                    .map(HeaderValue::from_maybe_shared)
                {
                    Some(Ok(v)) => Some(v),
                    _ => None,
                }
            })
        })
        .map(PyBuffer::from)
    }

    /// Returns a view of all values associated with a key.
    #[pyo3(signature = (key))]
    fn get_all<'py>(&self, py: Python<'py>, key: PyBackedStr) -> PyResult<Bound<'py, PyIterator>> {
        let values: Vec<_> = py.detach(|| {
            self.0
                .get_all::<&str>(key.as_ref())
                .iter()
                .cloned()
                .map(PyBuffer::from)
                .collect()
        });
        let pylist = PyList::new(py, values)?;
        PyIterator::from_object(&pylist)
    }

    /// Insert a key-value pair into the header map.
    #[pyo3(signature = (key, value))]
    fn insert(&mut self, py: Python, key: PyBackedStr, value: PyBackedStr) {
        py.detach(|| {
            if let (Ok(name), Ok(value)) = (
                HeaderName::from_bytes(key.as_bytes()),
                HeaderValue::from_maybe_shared(Bytes::from_owner(value)),
            ) {
                self.0.insert(name, value);
            }
        })
    }

    /// Append a key-value pair to the header map.
    #[pyo3(signature = (key, value))]
    fn append(&mut self, py: Python, key: PyBackedStr, value: PyBackedStr) {
        py.detach(|| {
            if let (Ok(name), Ok(value)) = (
                HeaderName::from_bytes(key.as_bytes()),
                HeaderValue::from_maybe_shared(Bytes::from_owner(value)),
            ) {
                self.0.append(name, value);
            }
        })
    }

    /// Remove a key-value pair from the header map.
    #[pyo3(signature = (key))]
    fn remove(&mut self, py: Python, key: PyBackedStr) {
        py.detach(|| {
            self.0.remove::<&str>(key.as_ref());
        })
    }

    /// Returns true if the map contains a value for the specified key.
    #[pyo3(signature = (key))]
    fn contains_key(&self, py: Python, key: PyBackedStr) -> bool {
        py.detach(|| self.0.contains_key::<&str>(key.as_ref()))
    }

    /// An iterator visiting all keys.
    #[inline]
    fn keys<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyIterator>> {
        let items = py.detach(|| {
            self.0
                .keys()
                .map(|k| PyBuffer::from(k.clone()))
                .collect::<Vec<_>>()
        });
        let pylist = PyList::new(py, items)?;
        PyIterator::from_object(&pylist)
    }

    ///  An iterator visiting all values.
    #[inline]
    fn values<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyIterator>> {
        let items = py.detach(|| {
            self.0
                .values()
                .map(|v| PyBuffer::from(v.clone()))
                .collect::<Vec<_>>()
        });
        let pylist = PyList::new(py, items)?;
        PyIterator::from_object(&pylist)
    }

    /// Returns the number of headers stored in the map.
    ///
    /// This number represents the total number of **values** stored in the map.
    /// This number can be greater than or equal to the number of **keys**
    /// stored given that a single key may have more than one associated value.
    #[inline]
    fn len(&self) -> usize {
        self.0.len()
    }

    /// Returns the number of keys stored in the map.
    ///
    /// This number will be less than or equal to `len()` as each key may have
    /// more than one associated value.
    #[inline]
    fn keys_len(&self) -> usize {
        self.0.keys_len()
    }

    /// Returns true if the map contains no elements.
    #[inline]
    fn is_empty(&self) -> bool {
        self.0.is_empty()
    }

    /// Clears the map, removing all key-value pairs. Keeps the allocated memory for reuse.
    #[inline]
    fn clear(&mut self) {
        self.0.clear();
    }
}

#[pymethods]
impl HeaderMap {
    #[inline]
    fn __getitem__<'py>(&self, py: Python<'py>, key: PyBackedStr) -> Option<PyBuffer> {
        self.get(py, key, None)
    }

    #[inline]
    fn __setitem__(&mut self, py: Python, key: PyBackedStr, value: PyBackedStr) {
        self.insert(py, key, value);
    }

    #[inline]
    fn __delitem__(&mut self, py: Python, key: PyBackedStr) {
        self.remove(py, key);
    }

    #[inline]
    fn __contains__(&self, py: Python, key: PyBackedStr) -> bool {
        self.contains_key(py, key)
    }

    #[inline]
    fn __len__(&self) -> usize {
        self.0.len()
    }

    fn __iter__<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyIterator>> {
        let items: Vec<_> = py.detach(|| {
            self.0
                .iter()
                .map(|(k, v)| (PyBuffer::from(k.clone()), PyBuffer::from(v.clone())))
                .collect()
        });
        let pylist = PyList::new(py, items)?;
        PyIterator::from_object(&pylist)
    }
}

impl fmt::Display for HeaderMap {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:?}", self.0)
    }
}

// ===== impl OrigHeaderMap =====

#[pymethods]
impl OrigHeaderMap {
    /// Creates a new `OrigHeaderMap` from an optional list of header names.
    #[new]
    #[pyo3(signature = (init=None, capacity=None))]
    fn new(init: Option<&Bound<'_, PyList>>, capacity: Option<usize>) -> OrigHeaderMap {
        let mut headers = capacity
            .map(header::OrigHeaderMap::with_capacity)
            .unwrap_or_default();

        // This section of memory might be retained by the Rust object,
        // and we want to prevent Python's garbage collector from managing it.
        if let Some(init) = init {
            for name in init.iter() {
                let name = match name
                    .extract::<PyBackedStr>()
                    .map(|n| HeaderName::from_bytes(n.as_bytes()))
                {
                    Ok(Ok(n)) => n,
                    _ => continue,
                };

                headers.insert(name);
            }
        }

        OrigHeaderMap(headers)
    }

    /// Insert a new header name into the collection.
    ///
    /// If the map did not previously have this key present, then `false` is
    /// returned.
    ///
    /// If the map did have this key present, the new value is pushed to the end
    /// of the list of values currently associated with the key. The key is not
    /// updated, though; this matters for types that can be `==` without being
    /// identical.
    #[inline]
    pub fn insert(&mut self, value: PyBackedStr) -> bool {
        self.0.insert(Bytes::from_owner(value))
    }

    /// Extends the map with all entries from another [`OrigHeaderMap`], preserving order.
    #[inline]
    pub fn extend(&mut self, iter: &Bound<'_, OrigHeaderMap>) {
        self.0.extend(iter.borrow().0.clone());
    }
}

#[pymethods]
impl OrigHeaderMap {
    #[inline]
    fn __len__(&self) -> usize {
        self.0.len()
    }

    fn __iter__<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyIterator>> {
        let items: Vec<_> = py.detach(|| {
            self.0
                .iter()
                .map(|(name, orig_name)| {
                    let name = PyBuffer::from(name.clone());
                    let orig_name = match orig_name.clone() {
                        header::OrigHeaderName::Cased(bytes) => PyBuffer::from(bytes),
                        header::OrigHeaderName::Standard(name) => PyBuffer::from(name),
                    };
                    (name, orig_name)
                })
                .collect()
        });
        let pylist = PyList::new(py, items)?;
        PyIterator::from_object(&pylist)
    }
}

impl fmt::Display for OrigHeaderMap {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{:?}", self.0)
    }
}
