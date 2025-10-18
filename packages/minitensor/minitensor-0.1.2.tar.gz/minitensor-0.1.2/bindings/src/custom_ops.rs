// Copyright (c) 2025 Soumyadip Sarkar.
// All rights reserved.
//
// This source code is licensed under the Apache-style license found in the
// LICENSE file in the root directory of this source tree.

use crate::error::_convert_error;
use crate::tensor::PyTensor;
use engine::custom_ops::{
    examples::register_example_ops, execute_custom_op, is_custom_op_registered, list_custom_ops,
    unregister_custom_op,
};
use pyo3::prelude::*;
use pyo3::types::PyList;

/// Register example custom operations
#[pyfunction]
fn register_example_custom_ops() -> PyResult<()> {
    register_example_ops().map_err(_convert_error)?;
    Ok(())
}

/// Unregister a custom operation
#[pyfunction]
fn unregister_custom_op_py(name: &str) -> PyResult<()> {
    unregister_custom_op(name).map_err(_convert_error)?;
    Ok(())
}

/// Execute a custom operation
#[pyfunction]
fn execute_custom_op_py(name: &str, inputs: &Bound<PyList>) -> PyResult<PyTensor> {
    // Convert Python list to vector of tensor references
    let mut tensor_refs = Vec::new();
    let mut tensors = Vec::new();

    for item in inputs.iter() {
        let py_tensor: PyTensor = match item.extract::<PyTensor>() {
            Ok(t) => t,
            Err(_) => {
                let inner = item.getattr("_tensor")?;
                inner.extract::<PyTensor>()?
            }
        };
        tensors.push(py_tensor.tensor().clone());
    }

    // Create references
    for tensor in &tensors {
        tensor_refs.push(tensor);
    }

    // Execute the operation
    let result = execute_custom_op(name, &tensor_refs).map_err(_convert_error)?;

    Ok(PyTensor::from_tensor(result))
}

/// List all registered custom operations
#[pyfunction]
fn list_custom_ops_py() -> PyResult<Vec<String>> {
    list_custom_ops().map_err(_convert_error)
}

/// Check if a custom operation is registered
#[pyfunction]
fn is_custom_op_registered_py(name: &str) -> PyResult<bool> {
    is_custom_op_registered(name).map_err(_convert_error)
}

/// Initialize the custom operations module
pub fn init_custom_ops_module(_py: Python, parent_module: &Bound<PyModule>) -> PyResult<()> {
    // Add functions to parent module
    parent_module.add_function(wrap_pyfunction!(
        register_example_custom_ops,
        parent_module
    )?)?;
    parent_module.add_function(wrap_pyfunction!(unregister_custom_op_py, parent_module)?)?;
    parent_module.add_function(wrap_pyfunction!(execute_custom_op_py, parent_module)?)?;
    parent_module.add_function(wrap_pyfunction!(list_custom_ops_py, parent_module)?)?;
    parent_module.add_function(wrap_pyfunction!(is_custom_op_registered_py, parent_module)?)?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use pyo3::Python;

    #[test]
    fn test_custom_ops_bindings() {
        pyo3::Python::initialize();
        Python::attach(|_| {
            // Test that we can call the functions without panicking
            let result = register_example_custom_ops();
            assert!(result.is_ok());

            let ops = list_custom_ops_py();
            assert!(ops.is_ok());

            let is_registered = is_custom_op_registered_py("swish");
            assert!(is_registered.is_ok());
        });
    }
}
