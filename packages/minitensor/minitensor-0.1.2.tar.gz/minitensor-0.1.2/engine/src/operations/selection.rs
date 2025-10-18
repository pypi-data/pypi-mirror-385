// Copyright (c) 2025 Soumyadip Sarkar.
// All rights reserved.
//
// This source code is licensed under the Apache-style license found in the
// LICENSE file in the root directory of this source tree.

use crate::{
    autograd::{WhereBackward, add_to_graph},
    device::Device,
    error::{MinitensorError, Result},
    operations::binary::{BinaryOpKind, coerce_binary_operands},
    tensor::{DataType, Shape, Strides, Tensor, TensorData},
};
use smallvec::{SmallVec, smallvec};
use std::sync::Arc;

/// Select elements from ``input`` or ``other`` based on ``condition``.
///
/// ``condition`` must be a boolean tensor. All tensors must reside on the same
/// device and have broadcastable shapes. The result has the broadcasted shape of
/// the three operands and takes values from ``input`` where ``condition`` is
/// true and from ``other`` where it is false.
pub fn where_op(condition: &Tensor, input: &Tensor, other: &Tensor) -> Result<Tensor> {
    if condition.device() != input.device() {
        return Err(MinitensorError::device_mismatch(
            format!("{:?}", condition.device()),
            format!("{:?}", input.device()),
        ));
    }
    if condition.device() != other.device() {
        return Err(MinitensorError::device_mismatch(
            format!("{:?}", condition.device()),
            format!("{:?}", other.device()),
        ));
    }
    if input.device() != other.device() {
        return Err(MinitensorError::device_mismatch(
            format!("{:?}", input.device()),
            format!("{:?}", other.device()),
        ));
    }

    if condition.dtype() != DataType::Bool {
        return Err(MinitensorError::invalid_operation(
            "where requires condition tensor of dtype bool",
        ));
    }

    let (input_cast, other_cast, result_dtype) =
        coerce_binary_operands(input, other, BinaryOpKind::Add)?;
    let input_tensor = input_cast.as_ref();
    let other_tensor = other_cast.as_ref();

    let tmp_shape = condition.shape().broadcast_with(input_tensor.shape())?;
    let output_shape = tmp_shape.broadcast_with(other_tensor.shape())?;

    let mut output_data = TensorData::uninitialized_on_device(
        output_shape.numel(),
        result_dtype,
        input_tensor.device(),
    );

    match result_dtype {
        DataType::Float32 => where_kernel(
            condition.data().as_bool_slice().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get bool slice from condition tensor")
            })?,
            input_tensor.data().as_f32_slice().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get f32 slice from input tensor")
            })?,
            other_tensor.data().as_f32_slice().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get f32 slice from other tensor")
            })?,
            output_data.as_f32_slice_mut().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get mutable f32 slice for where output")
            })?,
            condition.shape(),
            input_tensor.shape(),
            other_tensor.shape(),
            &output_shape,
        )?,
        DataType::Float64 => where_kernel(
            condition.data().as_bool_slice().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get bool slice from condition tensor")
            })?,
            input_tensor.data().as_f64_slice().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get f64 slice from input tensor")
            })?,
            other_tensor.data().as_f64_slice().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get f64 slice from other tensor")
            })?,
            output_data.as_f64_slice_mut().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get mutable f64 slice for where output")
            })?,
            condition.shape(),
            input_tensor.shape(),
            other_tensor.shape(),
            &output_shape,
        )?,
        DataType::Int32 => where_kernel(
            condition.data().as_bool_slice().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get bool slice from condition tensor")
            })?,
            input_tensor.data().as_i32_slice().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get i32 slice from input tensor")
            })?,
            other_tensor.data().as_i32_slice().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get i32 slice from other tensor")
            })?,
            output_data.as_i32_slice_mut().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get mutable i32 slice for where output")
            })?,
            condition.shape(),
            input_tensor.shape(),
            other_tensor.shape(),
            &output_shape,
        )?,
        DataType::Int64 => where_kernel(
            condition.data().as_bool_slice().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get bool slice from condition tensor")
            })?,
            input_tensor.data().as_i64_slice().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get i64 slice from input tensor")
            })?,
            other_tensor.data().as_i64_slice().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get i64 slice from other tensor")
            })?,
            output_data.as_i64_slice_mut().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get mutable i64 slice for where output")
            })?,
            condition.shape(),
            input_tensor.shape(),
            other_tensor.shape(),
            &output_shape,
        )?,
        DataType::Bool => where_kernel(
            condition.data().as_bool_slice().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get bool slice from condition tensor")
            })?,
            input_tensor.data().as_bool_slice().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get bool slice from input tensor")
            })?,
            other_tensor.data().as_bool_slice().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get bool slice from other tensor")
            })?,
            output_data.as_bool_slice_mut().ok_or_else(|| {
                MinitensorError::internal_error("Failed to get mutable bool slice for where output")
            })?,
            condition.shape(),
            input_tensor.shape(),
            other_tensor.shape(),
            &output_shape,
        )?,
    }

    let requires_grad = input.requires_grad() || other.requires_grad();
    let mut output = Tensor::new(
        Arc::new(output_data),
        output_shape.clone(),
        result_dtype,
        input_tensor.device(),
        requires_grad,
    );

    if requires_grad {
        let grad_fn = Arc::new(WhereBackward {
            condition: condition.detach(),
            input_shape: input.shape().dims().to_vec(),
            other_shape: other.shape().dims().to_vec(),
            input_requires_grad: input.requires_grad(),
            other_requires_grad: other.requires_grad(),
            input_ids: [input.id(), other.id()],
        });

        output.set_grad_fn(Some(grad_fn.clone()));
        add_to_graph(&output, Some(grad_fn))?;
    }

    Ok(output)
}

/// Fill elements of `input` where `mask` is `True` with values from `value`.
pub fn masked_fill(input: &Tensor, mask: &Tensor, value: &Tensor) -> Result<Tensor> {
    if mask.dtype() != DataType::Bool {
        return Err(MinitensorError::invalid_operation(
            "masked_fill mask must have bool dtype",
        ));
    }

    if input.device() != mask.device() {
        return Err(MinitensorError::device_mismatch(
            format!("{:?}", input.device()),
            format!("{:?}", mask.device()),
        ));
    }

    if input.device() != value.device() {
        return Err(MinitensorError::device_mismatch(
            format!("{:?}", input.device()),
            format!("{:?}", value.device()),
        ));
    }

    if input.dtype() != value.dtype() {
        return Err(MinitensorError::type_mismatch(
            format!("{:?}", input.dtype()),
            format!("{:?}", value.dtype()),
        ));
    }

    where_op(mask, value, input)
}

/// Scalar convenience for [`masked_fill`].
pub fn masked_fill_scalar(input: &Tensor, mask: &Tensor, value: f64) -> Result<Tensor> {
    let scalar = scalar_tensor(value, input.dtype(), input.device())?;
    masked_fill(input, mask, &scalar)
}

fn where_kernel<T: Copy>(
    condition: &[bool],
    input: &[T],
    other: &[T],
    output: &mut [T],
    condition_shape: &Shape,
    input_shape: &Shape,
    other_shape: &Shape,
    output_shape: &Shape,
) -> Result<()> {
    if output.is_empty() {
        return Ok(());
    }

    let output_dims = output_shape.dims();
    let rank = output_dims.len();

    let same_shape = condition_shape.dims() == output_dims
        && input_shape.dims() == output_dims
        && other_shape.dims() == output_dims
        && condition.len() == output.len()
        && input.len() == output.len()
        && other.len() == output.len();

    if same_shape {
        for ((out, &mask), (&lhs, &rhs)) in output
            .iter_mut()
            .zip(condition.iter())
            .zip(input.iter().zip(other.iter()))
        {
            *out = if mask { lhs } else { rhs };
        }
        return Ok(());
    }

    let cond_strides = Strides::from_shape(condition_shape);
    let input_strides = Strides::from_shape(input_shape);
    let other_strides = Strides::from_shape(other_shape);

    let cond_dims = condition_shape.dims();
    let input_dims = input_shape.dims();
    let other_dims = other_shape.dims();

    let cond_stride_slice = cond_strides.as_slice();
    let input_stride_slice = input_strides.as_slice();
    let other_stride_slice = other_strides.as_slice();

    let mut cond_aligned: SmallVec<[usize; 8]> = smallvec![0; rank];
    let mut input_aligned: SmallVec<[usize; 8]> = smallvec![0; rank];
    let mut other_aligned: SmallVec<[usize; 8]> = smallvec![0; rank];

    let cond_offset = rank.saturating_sub(cond_dims.len());
    for (i, &dim) in cond_dims.iter().enumerate() {
        cond_aligned[cond_offset + i] = if dim == 1 { 0 } else { cond_stride_slice[i] };
    }

    let input_offset = rank.saturating_sub(input_dims.len());
    for (i, &dim) in input_dims.iter().enumerate() {
        input_aligned[input_offset + i] = if dim == 1 { 0 } else { input_stride_slice[i] };
    }

    let other_offset = rank.saturating_sub(other_dims.len());
    for (i, &dim) in other_dims.iter().enumerate() {
        other_aligned[other_offset + i] = if dim == 1 { 0 } else { other_stride_slice[i] };
    }

    let cond_ptr = condition.as_ptr();
    let input_ptr = input.as_ptr();
    let other_ptr = other.as_ptr();

    for (idx, out) in output.iter_mut().enumerate() {
        let mut tmp = idx;
        let mut cond_index = 0usize;
        let mut input_index = 0usize;
        let mut other_index = 0usize;

        for dim in (0..rank).rev() {
            let coord = tmp % output_dims[dim];
            tmp /= output_dims[dim];

            cond_index += coord * cond_aligned[dim];
            input_index += coord * input_aligned[dim];
            other_index += coord * other_aligned[dim];
        }

        let mask = unsafe { *cond_ptr.add(cond_index) };
        let chosen = if mask {
            unsafe { *input_ptr.add(input_index) }
        } else {
            unsafe { *other_ptr.add(other_index) }
        };
        *out = chosen;
    }

    Ok(())
}

fn scalar_tensor(value: f64, dtype: DataType, device: Device) -> Result<Tensor> {
    let data = match dtype {
        DataType::Float32 => TensorData::from_vec_f32(vec![value as f32], device),
        DataType::Float64 => TensorData::from_vec_f64(vec![value], device),
        DataType::Int32 => TensorData::from_vec_i32(vec![value as i32], device),
        DataType::Int64 => TensorData::from_vec_i64(vec![value as i64], device),
        DataType::Bool => TensorData::from_vec_bool(vec![value != 0.0], device),
    };

    Ok(Tensor::new(
        Arc::new(data),
        Shape::scalar(),
        dtype,
        device,
        false,
    ))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{device::Device, tensor::TensorData};

    fn tensor_from_vec_bool(data: Vec<bool>, shape: Vec<usize>) -> Tensor {
        let shape = Shape::new(shape);
        let data = TensorData::from_vec_bool(data, Device::cpu());
        Tensor::new(Arc::new(data), shape, DataType::Bool, Device::cpu(), false)
    }

    fn tensor_from_vec_f32(data: Vec<f32>, shape: Vec<usize>) -> Tensor {
        let shape = Shape::new(shape);
        let data = TensorData::from_vec_f32(data, Device::cpu());
        Tensor::new(
            Arc::new(data),
            shape,
            DataType::Float32,
            Device::cpu(),
            false,
        )
    }

    fn tensor_from_vec_i32(data: Vec<i32>, shape: Vec<usize>) -> Tensor {
        let shape = Shape::new(shape);
        let data = TensorData::from_vec_i32(data, Device::cpu());
        Tensor::new(Arc::new(data), shape, DataType::Int32, Device::cpu(), false)
    }

    #[test]
    fn test_where_basic() {
        let condition = tensor_from_vec_bool(vec![true, false, true], vec![3]);
        let input = tensor_from_vec_f32(vec![1.0, 2.0, 3.0], vec![3]);
        let other = tensor_from_vec_f32(vec![10.0, 20.0, 30.0], vec![3]);

        let result = where_op(&condition, &input, &other).unwrap();
        let data = result.data().as_f32_slice().unwrap();
        assert_eq!(data, &[1.0, 20.0, 3.0]);
    }

    #[test]
    fn test_where_broadcasting() {
        let condition = tensor_from_vec_bool(vec![true, false], vec![2, 1]);
        let input = tensor_from_vec_f32(vec![1.0, 2.0, 3.0, 4.0], vec![2, 2]);
        let other = tensor_from_vec_f32(vec![10.0, 20.0], vec![1, 2]);

        let result = where_op(&condition, &input, &other).unwrap();
        let data = result.data().as_f32_slice().unwrap();
        assert_eq!(data, &[1.0, 2.0, 10.0, 20.0]);
        assert_eq!(result.shape().dims(), &[2, 2]);
    }

    #[test]
    fn test_where_condition_type_error() {
        let condition = tensor_from_vec_f32(vec![0.0, 1.0], vec![2]);
        let input = tensor_from_vec_f32(vec![1.0, 2.0], vec![2]);
        let other = tensor_from_vec_f32(vec![3.0, 4.0], vec![2]);
        assert!(where_op(&condition, &input, &other).is_err());
    }

    #[test]
    fn test_where_dtype_promotion() {
        let condition = tensor_from_vec_bool(vec![true, false], vec![2]);
        let input = Tensor::new(
            Arc::new(TensorData::from_vec_i64(vec![1, 2], Device::cpu())),
            Shape::new(vec![2]),
            DataType::Int64,
            Device::cpu(),
            false,
        );
        let other = tensor_from_vec_f32(vec![0.5, 1.5], vec![2]);

        let result = where_op(&condition, &input, &other).unwrap();
        assert_eq!(result.dtype(), DataType::Float32);
        let values = result.data().as_f32_slice().unwrap();
        assert_eq!(values, &[1.0, 1.5]);
    }

    #[test]
    fn test_masked_fill_scalar() {
        let input = tensor_from_vec_f32(vec![1.0, 2.0, 3.0], vec![3]);
        let mask = tensor_from_vec_bool(vec![true, false, true], vec![3]);

        let result = masked_fill_scalar(&input, &mask, 0.5).unwrap();
        let values = result.data().as_f32_slice().unwrap();
        assert_eq!(values, &[0.5, 2.0, 0.5]);
    }

    #[test]
    fn test_masked_fill_tensor_broadcast() {
        let input = tensor_from_vec_i32(vec![1, 2, 3, 4], vec![2, 2]);
        let mask = tensor_from_vec_bool(vec![true, false], vec![1, 2]);
        let fill = tensor_from_vec_i32(vec![9], vec![]);

        let result = masked_fill(&input, &mask, &fill).unwrap();
        let values = result.data().as_i32_slice().unwrap();
        assert_eq!(values, &[9, 2, 9, 4]);
    }
}
