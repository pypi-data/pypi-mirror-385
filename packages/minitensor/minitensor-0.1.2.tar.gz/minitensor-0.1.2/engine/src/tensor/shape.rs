// Copyright (c) 2025 Soumyadip Sarkar.
// All rights reserved.
//
// This source code is licensed under the Apache-style license found in the
// LICENSE file in the root directory of this source tree.

use crate::error::{MinitensorError, Result};
use serde::{Deserialize, Serialize};
use std::fmt;

/// Tensor shape representation
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct Shape {
    dims: Vec<usize>,
}

impl Shape {
    /// Create a new shape from dimensions
    #[inline(always)]
    pub fn new(dims: Vec<usize>) -> Self {
        Self { dims }
    }

    /// Create a scalar shape (0 dimensions)
    #[inline(always)]
    pub fn scalar() -> Self {
        Self { dims: vec![] }
    }

    /// Get the number of dimensions
    #[inline(always)]
    pub fn ndim(&self) -> usize {
        self.dims.len()
    }

    /// Get the total number of elements
    #[inline(always)]
    pub fn numel(&self) -> usize {
        if self.dims.is_empty() {
            1 // scalar
        } else {
            self.dims.iter().product()
        }
    }

    /// Get the size of a specific dimension
    #[inline(always)]
    pub fn size(&self, dim: usize) -> Result<usize> {
        self.dims
            .get(dim)
            .copied()
            .ok_or_else(|| MinitensorError::index_error(dim as isize, 0, self.dims.len()))
    }

    /// Get all dimensions as a slice
    #[inline(always)]
    pub fn dims(&self) -> &[usize] {
        &self.dims
    }

    /// Check if this is a scalar shape
    #[inline(always)]
    pub fn is_scalar(&self) -> bool {
        self.dims.is_empty()
    }

    /// Check if shapes are compatible for broadcasting
    #[inline(always)]
    pub fn is_broadcastable_with(&self, other: &Shape) -> bool {
        let max_ndim = self.ndim().max(other.ndim());

        // Compare dimensions from right to left (broadcasting rules)
        for i in 0..max_ndim {
            // Get dimension from the right (i=0 is rightmost)
            let self_dim = if i < self.ndim() {
                self.dims[self.ndim() - 1 - i]
            } else {
                1 // Implicit dimension of size 1
            };

            let other_dim = if i < other.ndim() {
                other.dims[other.ndim() - 1 - i]
            } else {
                1 // Implicit dimension of size 1
            };

            // Broadcasting rule: dimensions must be equal, or one must be 1
            if self_dim != other_dim && self_dim != 1 && other_dim != 1 {
                return false;
            }
        }

        true
    }

    /// Compute the broadcasted shape with another shape
    #[inline(always)]
    pub fn broadcast_with(&self, other: &Shape) -> Result<Shape> {
        if !self.is_broadcastable_with(other) {
            return Err(MinitensorError::shape_mismatch(
                self.dims.clone(),
                other.dims.clone(),
            ));
        }

        let max_ndim = self.ndim().max(other.ndim());
        let mut result_dims = Vec::with_capacity(max_ndim);

        for i in 0..max_ndim {
            let self_dim = if i < self.ndim() {
                self.dims[self.ndim() - 1 - i]
            } else {
                1
            };
            let other_dim = if i < other.ndim() {
                other.dims[other.ndim() - 1 - i]
            } else {
                1
            };

            let result_dim = if self_dim == other_dim {
                self_dim
            } else if self_dim == 1 {
                other_dim
            } else if other_dim == 1 {
                self_dim
            } else {
                // Due to the prior broadcastability check this branch should be
                // unreachable, but we keep it to ensure graceful error handling
                return Err(MinitensorError::shape_mismatch(
                    self.dims.clone(),
                    other.dims.clone(),
                ));
            };

            result_dims.push(result_dim);
        }

        result_dims.reverse();
        Ok(Shape::new(result_dims))
    }
}

impl fmt::Display for Shape {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "Shape({:?})", self.dims)
    }
}

impl From<Vec<usize>> for Shape {
    #[inline(always)]
    fn from(dims: Vec<usize>) -> Self {
        Self::new(dims)
    }
}

impl From<&[usize]> for Shape {
    #[inline(always)]
    fn from(dims: &[usize]) -> Self {
        Self::new(dims.to_vec())
    }
}

/// Memory strides for tensor data layout
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct Strides {
    strides: Vec<usize>,
}

impl Strides {
    /// Create new strides from a vector
    #[inline(always)]
    pub fn new(strides: Vec<usize>) -> Self {
        Self { strides }
    }

    /// Create contiguous strides from a shape
    #[inline(always)]
    pub fn from_shape(shape: &Shape) -> Self {
        let mut strides = Vec::with_capacity(shape.ndim());
        let mut stride = 1;

        for &dim in shape.dims().iter().rev() {
            strides.push(stride);
            stride *= dim;
        }

        strides.reverse();
        Self { strides }
    }

    /// Get the strides as a slice
    #[inline(always)]
    pub fn as_slice(&self) -> &[usize] {
        &self.strides
    }

    /// Check if the strides represent a contiguous layout
    #[inline(always)]
    pub fn is_contiguous(&self, shape: &Shape) -> bool {
        if self.strides.len() != shape.ndim() {
            return false;
        }

        let mut expected_stride = 1;
        for (i, &dim) in shape.dims().iter().enumerate().rev() {
            if self.strides[i] != expected_stride {
                return false;
            }
            expected_stride *= dim;
        }

        true
    }

    /// Compute the linear index from multi-dimensional indices
    #[inline(always)]
    pub fn linear_index(&self, indices: &[usize]) -> usize {
        indices
            .iter()
            .zip(self.strides.iter())
            .map(|(&idx, &stride)| idx * stride)
            .sum()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_shape_creation() {
        let shape = Shape::new(vec![2, 3, 4]);
        assert_eq!(shape.ndim(), 3);
        assert_eq!(shape.numel(), 24);
        assert_eq!(shape.size(0).unwrap(), 2);
        assert_eq!(shape.size(1).unwrap(), 3);
        assert_eq!(shape.size(2).unwrap(), 4);
        assert!(!shape.is_scalar());

        let scalar = Shape::scalar();
        assert_eq!(scalar.ndim(), 0);
        assert_eq!(scalar.numel(), 1);
        assert!(scalar.is_scalar());
    }

    #[test]
    fn test_broadcasting() {
        let shape1 = Shape::new(vec![3, 1]);
        let shape2 = Shape::new(vec![1, 4]);

        assert!(shape1.is_broadcastable_with(&shape2));

        let broadcasted = shape1.broadcast_with(&shape2).unwrap();
        assert_eq!(broadcasted.dims(), &[3, 4]);
    }

    #[test]
    fn test_strides() {
        let shape = Shape::new(vec![2, 3, 4]);
        let strides = Strides::from_shape(&shape);

        assert_eq!(strides.as_slice(), &[12, 4, 1]);
        assert!(strides.is_contiguous(&shape));

        let linear_idx = strides.linear_index(&[1, 2, 3]);
        assert_eq!(linear_idx, 1 * 12 + 2 * 4 + 3 * 1);
    }

    #[test]
    fn test_broadcasting_incompatible() {
        let shape1 = Shape::new(vec![2, 3]);
        let shape2 = Shape::new(vec![3, 4]);
        assert!(!shape1.is_broadcastable_with(&shape2));
        assert!(shape1.broadcast_with(&shape2).is_err());
    }

    #[test]
    fn test_size_out_of_bounds() {
        let shape = Shape::new(vec![2, 3]);
        assert!(shape.size(2).is_err());
    }

    #[test]
    fn test_non_contiguous_and_mismatched_strides() {
        let shape = Shape::new(vec![2, 3]);
        let bad = Strides::new(vec![2, 1]);
        assert!(!bad.is_contiguous(&shape));
        let mismatched = Strides::new(vec![1]);
        assert!(!mismatched.is_contiguous(&shape));
    }

    #[test]
    fn test_scalar_strides_behavior() {
        let shape = Shape::scalar();
        let strides = Strides::from_shape(&shape);
        assert!(strides.as_slice().is_empty());
        assert!(strides.is_contiguous(&shape));
        assert_eq!(strides.linear_index(&[]), 0);
    }

    #[test]
    fn test_broadcast_with_scalar_shape() {
        let scalar = Shape::scalar();
        let other = Shape::new(vec![2, 3]);
        assert!(scalar.is_broadcastable_with(&other));
        let broadcasted = scalar.broadcast_with(&other).unwrap();
        assert_eq!(broadcasted.dims(), &[2, 3]);
    }

    #[test]
    fn test_broadcast_different_dimensions() {
        let shape1 = Shape::new(vec![1, 2, 3]);
        let shape2 = Shape::new(vec![3]);
        assert!(shape1.is_broadcastable_with(&shape2));
        let broadcasted = shape1.broadcast_with(&shape2).unwrap();
        assert_eq!(broadcasted.dims(), &[1, 2, 3]);
    }

    #[test]
    fn test_numel_with_zero_dim() {
        let shape = Shape::new(vec![2, 0, 4]);
        assert_eq!(shape.numel(), 0);
    }

    #[test]
    fn test_broadcasting_with_zero_dim() {
        let shape1 = Shape::new(vec![2, 0, 4]);
        let shape2 = Shape::new(vec![1, 0, 1]);
        assert!(shape1.is_broadcastable_with(&shape2));
        let broadcasted = shape1.broadcast_with(&shape2).unwrap();
        assert_eq!(broadcasted.dims(), &[2, 0, 4]);

        let shape3 = Shape::new(vec![2, 2, 4]);
        assert!(!shape1.is_broadcastable_with(&shape3));
        assert!(shape1.broadcast_with(&shape3).is_err());
    }
}
