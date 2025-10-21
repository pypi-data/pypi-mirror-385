// Copyright (c) 2025 Junior Sundar
//
// SPDX-License-Identifier: BSD-3-Clause

use pyo3::{prelude::*, types::PyList};
use std::{rc::Rc, sync::Arc};

use super::{
    compound_state::PyCompoundState, real_vector_state::PyRealVectorState, se2_state::PySE2State,
    se3_state::PySE3State, so2_state::PySO2State, so3_state::PySO3State,
};
use oxmpl::base::{
    planner::Path as OxmplPath,
    state::{
        CompoundState as OxmplCompoundState, RealVectorState as OxmplRealVectorState,
        SE2State as OxmplSE2State, SE3State as OxmplSE3State, SO2State as OxmplSO2State,
        SO3State as OxmplSO3State,
    },
};

#[derive(Clone)]
pub enum PathVariant {
    RealVector(OxmplPath<OxmplRealVectorState>),
    SO2(OxmplPath<OxmplSO2State>),
    SO3(OxmplPath<OxmplSO3State>),
    Compound(OxmplPath<OxmplCompoundState>),
    SE2(OxmplPath<OxmplSE2State>),
    SE3(OxmplPath<OxmplSE3State>),
}

/// A sequence of states representing a solution path found by a planner.
#[pyclass(name = "Path", unsendable)]
#[derive(Clone)]
pub struct PyPath(pub PathVariant);

#[pymethods]
impl PyPath {
    /// Creates a new Path object from a list of `RealVectorState` objects.
    #[staticmethod]
    fn from_real_vector_states(states: Vec<PyRealVectorState>) -> Self {
        let rust_states = states.into_iter().map(|s| (*s.0).clone()).collect();
        Self(PathVariant::RealVector(OxmplPath(rust_states)))
    }

    /// Creates a new Path from a list of `SO2State` objects.
    #[staticmethod]
    fn from_so2_states(states: Vec<PySO2State>) -> Self {
        let rust_states = states.into_iter().map(|s| (*s.0).clone()).collect();
        Self(PathVariant::SO2(OxmplPath(rust_states)))
    }

    /// Creates a new Path from a list of `SO3State` objects.
    #[staticmethod]
    fn from_so3_states(states: Vec<PySO3State>) -> Self {
        let rust_states = states.into_iter().map(|s| (*s.0).clone()).collect();
        Self(PathVariant::SO3(OxmplPath(rust_states)))
    }

    /// Creates a new Path from a list of `CompoundState` objects.
    #[staticmethod]
    fn from_compound_states(states: Vec<PyCompoundState>) -> Self {
        let rust_states = states.into_iter().map(|s| (*s.0).clone()).collect();
        Self(PathVariant::Compound(OxmplPath(rust_states)))
    }

    /// Creates a new Path from a list of `SE2State` objects.
    #[staticmethod]
    fn from_se2_states(states: Vec<PySE2State>) -> Self {
        let rust_states = states.into_iter().map(|s| (*s.0).clone()).collect();
        Self(PathVariant::SE2(OxmplPath(rust_states)))
    }

    /// Creates a new Path from a list of `SE3State` objects.
    #[staticmethod]
    fn from_se3_states(states: Vec<PySE3State>) -> Self {
        let rust_states = states.into_iter().map(|s| (*s.0).clone()).collect();
        Self(PathVariant::SE3(OxmplPath(rust_states)))
    }

    /// list[]: The sequence of states that make up the path.
    #[getter]
    fn get_states(&self, py: Python<'_>) -> PyResult<PyObject> {
        let py_list = match &self.0 {
            PathVariant::RealVector(path) => {
                let list = PyList::empty(py);
                for s in &path.0 {
                    let py_state = PyRealVectorState(Arc::new(s.clone()));
                    let obj = py_state.into_pyobject(py)?; // Bound<PyAny>
                    list.append(obj)?;
                }
                list
            }
            PathVariant::SO2(path) => {
                let list = PyList::empty(py);
                for s in &path.0 {
                    let py_state = PySO2State(Arc::new(s.clone()));
                    let obj = py_state.into_pyobject(py)?;
                    list.append(obj)?;
                }
                list
            }
            PathVariant::SO3(path) => {
                let list = PyList::empty(py);
                for s in &path.0 {
                    let py_state = PySO3State(Arc::new(s.clone()));
                    let obj = py_state.into_pyobject(py)?;
                    list.append(obj)?;
                }
                list
            }
            PathVariant::Compound(path) => {
                let list = PyList::empty(py);
                for s in &path.0 {
                    let py_state = PyCompoundState(Rc::new(s.clone()));
                    let obj = py_state.into_pyobject(py)?;
                    list.append(obj)?;
                }
                list
            }
            PathVariant::SE2(path) => {
                let list = PyList::empty(py);
                for s in &path.0 {
                    let py_state = PySE2State(Rc::new(s.clone()));
                    let obj = py_state.into_pyobject(py)?;
                    list.append(obj)?;
                }
                list
            }
            PathVariant::SE3(path) => {
                let list = PyList::empty(py);
                for s in &path.0 {
                    let py_state = PySE3State(Rc::new(s.clone()));
                    let obj = py_state.into_pyobject(py)?;
                    list.append(obj)?;
                }
                list
            }
        };
        Ok(py_list.into())
    }

    /// The number of states in the path.
    fn __len__(&self) -> usize {
        match &self.0 {
            PathVariant::RealVector(path) => path.0.len(),
            PathVariant::SO2(path) => path.0.len(),
            PathVariant::SO3(path) => path.0.len(),
            PathVariant::Compound(path) => path.0.len(),
            PathVariant::SE2(path) => path.0.len(),
            PathVariant::SE3(path) => path.0.len(),
        }
    }

    fn __repr__(&self) -> String {
        let (len, type_name) = match &self.0 {
            PathVariant::RealVector(path) => (path.0.len(), "RealVectorState"),
            PathVariant::SO2(path) => (path.0.len(), "SO2State"),
            PathVariant::SO3(path) => (path.0.len(), "SO3State"),
            PathVariant::Compound(path) => (path.0.len(), "CompoundState"),
            PathVariant::SE2(path) => (path.0.len(), "SE2State"),
            PathVariant::SE3(path) => (path.0.len(), "SE3State"),
        };
        format!("<Path of {len} {type_name}s>")
    }
}

impl From<OxmplPath<OxmplRealVectorState>> for PyPath {
    fn from(path: OxmplPath<OxmplRealVectorState>) -> Self {
        Self(PathVariant::RealVector(path))
    }
}

impl From<OxmplPath<OxmplSO2State>> for PyPath {
    fn from(path: OxmplPath<OxmplSO2State>) -> Self {
        Self(PathVariant::SO2(path))
    }
}

impl From<OxmplPath<OxmplSO3State>> for PyPath {
    fn from(path: OxmplPath<OxmplSO3State>) -> Self {
        Self(PathVariant::SO3(path))
    }
}

impl From<OxmplPath<OxmplCompoundState>> for PyPath {
    fn from(path: OxmplPath<OxmplCompoundState>) -> Self {
        Self(PathVariant::Compound(path))
    }
}

impl From<OxmplPath<OxmplSE2State>> for PyPath {
    fn from(path: OxmplPath<OxmplSE2State>) -> Self {
        Self(PathVariant::SE2(path))
    }
}

impl From<OxmplPath<OxmplSE3State>> for PyPath {
    fn from(path: OxmplPath<OxmplSE3State>) -> Self {
        Self(PathVariant::SE3(path))
    }
}
