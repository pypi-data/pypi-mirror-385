# ===----------------------------------------------------------------------=== #
# Nabla 2025
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===----------------------------------------------------------------------=== #

"""View and shape manipulation operations."""

import numpy as np
from max.dtype import DType
from max.graph import TensorValue, ops

from ..core.tensor import Tensor, Shape
from .operation import Operation, ViewOperation

# Public API
__all__ = [
    "transpose",
    "permute",
    "move_axis_to_front",
    "move_axis_from_front",
    "permute_batch_dims",
    "move_axis_to_front_of_batch_dims",
    "move_axis_from_front_of_batch_dims",
    "reshape",
    "broadcast_to",
    "broadcast_batch_dims",
    "squeeze",
    "unsqueeze",
    "squeeze_batch_dims",
    "unsqueeze_batch_dims",
    "shallow_copy",
    "tensor_slice",
    "pad",
    "concatenate",
    "stack",
]


class TransposeOp(ViewOperation):
    """Matrix/tensor transpose operation."""

    def __init__(self, axis_1: int = -2, axis_2: int = -1):
        super().__init__(f"transpose[permutation=({axis_1},{axis_2})]")
        self.axis_1 = axis_1
        self.axis_2 = axis_2

    def compute_output_shape(self, *input_shapes: tuple) -> tuple:
        """Compute output shape for transpose operation with compatible signature."""
        if len(input_shapes) != 1:
            raise ValueError(
                f"Transpose operation requires 1 input shape, got {len(input_shapes)}"
            )
        arg_shape = input_shapes[0]

        if not arg_shape:
            # Transposing a scalar is a no-op.
            return ()

        # For rank 1, transpose is also a no-op.
        if len(arg_shape) < 2:
            return arg_shape

        axis_1 = self.axis_1 if self.axis_1 >= 0 else len(arg_shape) + self.axis_1
        axis_2 = self.axis_2 if self.axis_2 >= 0 else len(arg_shape) + self.axis_2

        if axis_1 < 0 or axis_1 >= len(arg_shape):
            raise ValueError(f"axis_1 {axis_1} is out of bounds for shape {arg_shape}")
        if axis_2 < 0 or axis_2 >= len(arg_shape):
            raise ValueError(f"axis_2 {axis_2} is out of bounds for shape {arg_shape}")

        new_shape = list(arg_shape)
        new_shape[axis_1], new_shape[axis_2] = new_shape[axis_2], new_shape[axis_1]
        return tuple(new_shape)

    def maxpr(self, args: list[TensorValue], output: Tensor) -> None:
        if len(args[0].shape) < 2:
            output.tensor_value = args[0]
            return
        output.tensor_value = ops.transpose(args[0], self.axis_1, self.axis_2)

    def eagerxpr(self, args: list[Tensor], output: Tensor) -> None:
        if len(args[0].shape) < 2:
            output._impl = args[0].impl
            return

        offset = len(args[0].batch_dims)
        axes = list(range(-offset - len(args[0].shape), 0))
        axes[self.axis_1], axes[self.axis_2] = axes[self.axis_2], axes[self.axis_1]

        np_result = np.transpose(args[0].to_numpy(), axes)
        output.impl_(np_result)

    def vjp_rule(
        self, primals: list[Tensor], cotangent: Tensor, output: Tensor
    ) -> list[Tensor]:
        return [transpose(cotangent, self.axis_1, self.axis_2)]

    def jvp_rule(
        self, primals: list[Tensor], tangents: list[Tensor], output: Tensor
    ) -> Tensor:
        return transpose(tangents[0], self.axis_1, self.axis_2)


def transpose(arg: Tensor, axis_1: int = -2, axis_2: int = -1) -> Tensor:
    """Transpose tensor along two axes."""
    if len(arg.shape) <= 1:
        return arg

    axis_1 = axis_1 if axis_1 < 0 else -len(arg.shape) + axis_1
    axis_2 = axis_2 if axis_2 < 0 else -len(arg.shape) + axis_2
    if axis_1 == axis_2:
        return arg
    if axis_1 < -len(arg.shape) or axis_2 < -len(arg.shape):
        raise ValueError(
            f"Invalid axes {axis_1}, {axis_2} for shape {arg.shape}. "
            "Axes must be within the range of the tensor dimensions."
        )

    op = TransposeOp(axis_1, axis_2)
    return op.forward(arg)


class TransposeBatchDimsOp(ViewOperation):
    """Transpose operation to swap two batch dimensions."""

    def __init__(self, axis_1: int = -2, axis_2: int = -1):
        """Initialize transpose batch dims operation.

        Parameters
    ----------
            axis_1: First batch dimension axis to swap (negative indices preferred)
            axis_2: Second batch dimension axis to swap (negative indices preferred)
        """
        super().__init__(f"transpose_batch_dims[permutation=({axis_1},{axis_2})]")
        self.axis_1 = axis_1
        self.axis_2 = axis_2

    def compute_output_shape(self, *input_shapes: tuple) -> tuple:
        """Shape stays the same for batch dimension operations."""
        if len(input_shapes) != 1:
            raise ValueError(
                f"Transpose batch dims operation requires 1 input shape, got {len(input_shapes)}"
            )
        return input_shapes[0]

    def compute_output_batch_dims(self, *input_batch_dimss: tuple) -> tuple:
        """Compute output batch_dims after transposing two axes."""
        if len(input_batch_dimss) != 1:
            raise ValueError(
                f"Transpose batch dims operation requires 1 input batch_dims, got {len(input_batch_dimss)}"
            )
        input_batch_dims = input_batch_dimss[0]

        if not input_batch_dims:
            raise ValueError(
                "Cannot transpose batch dims of an tensor with no batch dimensions"
            )

        # Convert negative indices to positive for validation and computation
        axis_1 = self.axis_1 + len(input_batch_dims) if self.axis_1 < 0 else self.axis_1
        axis_2 = self.axis_2 + len(input_batch_dims) if self.axis_2 < 0 else self.axis_2

        # Validate axes are within bounds
        if axis_1 < 0 or axis_1 >= len(input_batch_dims):
            raise ValueError(
                f"axis_1 {self.axis_1} is out of bounds for batch_dims {input_batch_dims}"
            )
        if axis_2 < 0 or axis_2 >= len(input_batch_dims):
            raise ValueError(
                f"axis_2 {self.axis_2} is out of bounds for batch_dims {input_batch_dims}"
            )

        # Create new batch_dims with axes swapped
        new_batch_dims = list(input_batch_dims)
        new_batch_dims[axis_1], new_batch_dims[axis_2] = (
            new_batch_dims[axis_2],
            new_batch_dims[axis_1],
        )

        return tuple(new_batch_dims)

    def forward(self, *args: Tensor) -> Tensor:
        """Override forward to handle single input."""
        if len(args) != 1:
            raise ValueError(
                f"Transpose batch dims operation requires 1 argument, got {len(args)}"
            )
        return super().forward(*args)

    def maxpr(self, args: list[TensorValue], output: Tensor) -> None:
        """MAX graph implementation using ops.transpose."""
        axis_1 = self.axis_1 - len(output.shape)
        axis_2 = self.axis_2 - len(output.shape)

        output.tensor_value = ops.transpose(args[0], axis_1, axis_2)

    def eagerxpr(self, args: list[Tensor], output: Tensor) -> None:
        """Eager execution using NumPy transpose."""
        input_tensor = args[0]

        # Get the full tensor including batch dimensions
        input_np = input_tensor.to_numpy()

        axis_1 = self.axis_1 - len(args[0].shape)
        axis_2 = self.axis_2 - len(args[0].shape)

        # Create axes list for full transpose
        total_dims = len(input_tensor.batch_dims) + len(input_tensor.shape)
        axes = list(range(total_dims))

        # Swap the two batch dimension axes
        axes[axis_1], axes[axis_2] = axes[axis_2], axes[axis_1]

        # Apply transpose
        np_result = np.transpose(input_np, axes)
        output.impl_(np_result)

    def vjp_rule(
        self, primals: list[Tensor], cotangent: Tensor, output: Tensor
    ) -> list[Tensor]:
        """VJP rule: transpose is its own inverse."""
        return [transpose_batch_dims(cotangent, self.axis_1, self.axis_2)]

    def jvp_rule(
        self, primals: list[Tensor], tangents: list[Tensor], output: Tensor
    ) -> Tensor:
        """JVP rule: apply same transpose to tangents."""
        return transpose_batch_dims(tangents[0], self.axis_1, self.axis_2)


def transpose_batch_dims(arg: Tensor, axis_1: int = -2, axis_2: int = -1) -> Tensor:
    """Transpose batch dimensions along two axes.

    This operation swaps two axes in the batch_dims of an Tensor, similar to how
    regular transpose works on shape dimensions. The shape dimensions remain unchanged.

    Parameters
    ----------
        arg: Input tensor with batch dimensions to transpose
        axis_1: First batch dimension axis to swap (default: -2)
        axis_2: Second batch dimension axis to swap (default: -1)

    Returns
    -------
        Tensor with specified batch dimensions transposed

    Examples
    --------
        >>> import nabla as nb
        >>> # Tensor with batch_dims=(2, 3, 4) and shape=(5, 6)
        >>> x = nb.ones((5, 6))
        >>> x.batch_dims = (2, 3, 4)  # Simulated for example
        >>> y = transpose_batch_dims(x, -3, -1)  # Swap first and last batch dims
        >>> # Result has batch_dims=(4, 3, 2) and shape=(5, 6)
    """
    # Convert to negative indices for consistency with batch dimension handling
    axis_1 = axis_1 if axis_1 < 0 else -len(arg.batch_dims) + axis_1
    axis_2 = axis_2 if axis_2 < 0 else -len(arg.batch_dims) + axis_2

    op = TransposeBatchDimsOp(axis_1, axis_2)
    return op.forward(arg)


def compute_iterative_transpose_swaps(axes: tuple[int, ...]) -> list[tuple[int, int]]:
    """Compute the sequence of axis swaps needed to implement a permutation.

    This function implements the algorithm from the Mojo code to determine what
    sequence of axis swaps (transposes) are needed to achieve a given permutation.
    Returns a list of (axis1, axis2) tuples that should be swapped in order.

    Parameters
    ----------
        axes: Tuple of axis indices specifying the desired permutation.
              All indices should be negative (e.g., -1, -2, -3, ...)

    Returns
    -------
        List of (axis1, axis2) tuples representing the swaps to perform in order.
        Each tuple contains two negative axis indices to be swapped.

    The algorithm works as follows:
    1. Initialize current_axis_order as [-num_dims, -num_dims+1, ..., -1]
    2. For each target position x, find where target_axis currently is (y)
    3. If x != y, record the swap (x_neg, y_neg) and update current_axis_order
    4. Return the list of all recorded swaps
    """
    target_perm = list(axes)
    num_dims = len(target_perm)

    # Initialize current_axis_order as in Mojo: [-num_dims, -num_dims+1, ..., -1]
    current_axis_order = []
    for i in range(-num_dims, 0):
        current_axis_order.append(i)

    swaps = []

    # For each target position x, move the correct axis there
    for x in range(num_dims):
        target_axis = target_perm[x]

        # Find where target_axis currently is in the current ordering
        try:
            y = current_axis_order.index(target_axis)
        except ValueError as e:
            # target_axis not found in current_axis_order, this shouldn't happen
            raise ValueError(
                f"Target axis {target_axis} not found in current_axis_order {current_axis_order}"
            ) from e

        # If already in the right position, skip
        if x == y:
            continue

        # Convert to negative indices for the swap operation
        x_neg = x - num_dims
        y_neg = y - num_dims

        # Record the swap
        swaps.append((x_neg, y_neg))

        # Update current_axis_order to reflect the swap
        # Swap the elements at positions x and y
        current_axis_order[x], current_axis_order[y] = (
            current_axis_order[y],
            current_axis_order[x],
        )

    return swaps


class PermuteOp(ViewOperation):
    """Permute (reorder) the dimensions of a tensor according to given axes."""

    def __init__(self, axes: tuple[int, ...]):
        """Initialize permute operation.

        Parameters
    ----------
            axes: Tuple of axis indices specifying the new order.
                  Must be a permutation of range(ndim).
        """
        super().__init__(f"permute[axes={axes}]")
        self.axes = tuple(axes)

    def compute_output_shape(self, *input_shapes: tuple) -> tuple:
        """Compute output shape after permutation."""
        if len(input_shapes) != 1:
            raise ValueError(
                f"Permute operation requires 1 input shape, got {len(input_shapes)}"
            )

        input_shape = input_shapes[0]

        # Validate axes - should now be all negative and same length as input
        if len(self.axes) != len(input_shape):
            raise ValueError(
                f"Number of axes {len(self.axes)} must match input dimensions {len(input_shape)}"
            )

        # Convert to positive indices for validation
        positive_axes = [ax + len(input_shape) for ax in self.axes]
        if sorted(positive_axes) != list(range(len(input_shape))):
            raise ValueError(
                f"Axes {self.axes} must be a permutation of negative indices corresponding to {list(range(len(input_shape)))}"
            )

        # Reorder dimensions according to axes (convert negative to positive for indexing)
        return tuple(input_shape[axis + len(input_shape)] for axis in self.axes)

    def maxpr(self, args: list[TensorValue], output: Tensor) -> None:
        """Max computation: permute the tensor using iterative transpose."""
        # Get the sequence of swaps needed for this permutation
        swaps = compute_iterative_transpose_swaps(self.axes)

        # Apply each swap in sequence
        out_symbol = args[0]
        for axis1, axis2 in swaps:
            out_symbol = ops.transpose(out_symbol, axis1, axis2)

        output.tensor_value = out_symbol

    def eagerxpr(self, args: list[Tensor], output: Tensor) -> None:
        """Eager computation: permute using numpy."""
        # Handle batch dimensions properly like transpose does
        offset = len(args[0].batch_dims)

        # Convert our negative axes (relative to tensor shape) to work with full numpy tensor
        numpy_axes = []
        for ax in self.axes:
            # ax is negative relative to args[0].shape, convert to positive
            tensor_pos_ax = ax + len(args[0].shape)
            # Now convert to position in full numpy tensor (including batch dims)
            numpy_pos_ax = offset + tensor_pos_ax
            numpy_axes.append(numpy_pos_ax)

        # Prepend batch dimension indices (they stay in their original positions)
        full_axes = list(range(offset)) + numpy_axes

        np_result = np.transpose(args[0].to_numpy(), full_axes)
        output.impl_(np_result)

    def vjp_rule(
        self, primals: list[Tensor], cotangent: Tensor, output: Tensor
    ) -> list[Tensor]:
        """VJP rule: reverse the permutation."""
        # Create inverse permutation for negative indices
        inv_axes = [0] * len(self.axes)
        for i, axis in enumerate(self.axes):
            # Convert negative axis to positive index for inverse mapping
            pos_axis = axis + len(self.axes)
            inv_axes[pos_axis] = i

        # Convert back to negative indices
        inv_axes_negative = [-len(self.axes) + ax for ax in inv_axes]

        return [permute(cotangent, tuple(inv_axes_negative))]

    def jvp_rule(
        self, primals: list[Tensor], tangents: list[Tensor], output: Tensor
    ) -> Tensor:
        """JVP rule: apply same permutation to tangent."""
        return permute(tangents[0], self.axes)


def permute(input_tensor: Tensor, axes: tuple[int, ...]) -> Tensor:
    """Permute (reorder) the dimensions of a tensor.

    Parameters
    ----------
        input_tensor: Input tensor
        axes: Tuple specifying the new order of dimensions

    Returns
    -------
        Tensor with reordered dimensions

    Examples
    --------
        >>> x = nb.ones((2, 3, 4))  # shape (2, 3, 4)
        >>> y = permute(x, (2, 0, 1))  # shape (4, 2, 3)
        >>> # Dimension 2 -> position 0, dimension 0 -> position 1, dimension 1 -> position 2
    """
    # always store axes to be fully negative
    axes = tuple(-len(input_tensor.shape) + ax if ax >= 0 else ax for ax in axes)
    # but first we add oentailly missing axes which we treat as unpemruted
    axes_new = []
    for i in range(-len(input_tensor.shape), -len(axes)):
        axes_new.append(i)

    axes = tuple(axes_new + list(axes))  # prepend missing axes to the front

    op = PermuteOp(axes)
    return op.forward(input_tensor)


class PermuteBatchDimsOp(ViewOperation):
    """Permute (reorder) the batch dimensions of an tensor according to given axes."""

    def __init__(self, axes: tuple[int, ...]):
        """Initialize permute batch dims operation.

        Parameters
    ----------
            axes: Tuple of axis indices specifying the new order for batch_dims.
                  Must be a permutation of range(-len(batch_dims), 0).
                  All indices should be negative.
        """
        super().__init__(f"permute_batch_dims[axes={axes}]")
        self.axes = tuple(axes)

    def compute_output_shape(self, *input_shapes: tuple) -> tuple:
        """Shape stays the same for batch dimension operations."""
        if len(input_shapes) != 1:
            raise ValueError(
                f"Permute batch dims operation requires 1 input shape, got {len(input_shapes)}"
            )
        return input_shapes[0]

    def compute_output_batch_dims(self, *input_batch_dimss: tuple) -> tuple:
        """Compute output batch_dims after permutation."""
        if len(input_batch_dimss) != 1:
            raise ValueError(
                f"Permute batch dims operation requires 1 input batch_dims, got {len(input_batch_dimss)}"
            )
        input_batch_dims = input_batch_dimss[0]

        if not input_batch_dims:
            raise ValueError(
                "Cannot permute batch dims of an tensor with no batch dimensions"
            )

        # Validate axes - should be all negative and same length as input batch_dims
        if len(self.axes) != len(input_batch_dims):
            raise ValueError(
                f"Number of axes {len(self.axes)} must match input batch dimensions {len(input_batch_dims)}"
            )

        # Convert to positive indices for validation
        positive_axes = [ax + len(input_batch_dims) for ax in self.axes]
        if sorted(positive_axes) != list(range(len(input_batch_dims))):
            raise ValueError(
                f"Axes {self.axes} must be a permutation of negative indices corresponding to batch_dims range"
            )

        # Reorder batch dimensions according to axes (convert negative to positive for indexing)
        return tuple(
            input_batch_dims[axis + len(input_batch_dims)] for axis in self.axes
        )

    def forward(self, *args: Tensor) -> Tensor:
        """Override forward to handle single input."""
        if len(args) != 1:
            raise ValueError(
                f"Permute batch dims operation requires 1 argument, got {len(args)}"
            )
        return super().forward(*args)

    def maxpr(self, args: list[TensorValue], output: Tensor) -> None:
        """MAX graph implementation using ops.transpose."""
        # Get the sequence of swaps needed for this permutation
        swaps = compute_iterative_transpose_swaps(self.axes)
        swaps = [
            (axis1 - len(output.shape), axis2 - len(output.shape))
            for axis1, axis2 in swaps
        ]

        # Apply each swap in sequence
        out_symbol = args[0]
        for axis1, axis2 in swaps:
            out_symbol = ops.transpose(out_symbol, axis1, axis2)

        output.tensor_value = out_symbol

    def eagerxpr(self, args: list[Tensor], output: Tensor) -> None:
        """Eager execution using NumPy transpose."""
        input_tensor = args[0]

        # Get the full tensor including batch dimensions
        input_np = input_tensor.to_numpy()

        # Convert batch dimension axes to full tensor indices
        # Following the pattern from other batch operations
        numpy_axes = []
        for ax in self.axes:
            # ax is negative relative to batch_dims, convert to full tensor position
            batch_pos_ax = ax - len(input_tensor.shape)
            numpy_axes.append(batch_pos_ax)

        # Add shape dimension indices (they stay in their original relative positions)
        # They come after the batch dimensions in the permuted tensor
        shape_offset = len(input_tensor.batch_dims)
        shape_axes = list(range(shape_offset, shape_offset + len(input_tensor.shape)))
        full_axes = numpy_axes + shape_axes

        # Apply transpose
        np_result = np.transpose(input_np, full_axes)
        output.impl_(np_result)

    def vjp_rule(
        self, primals: list[Tensor], cotangent: Tensor, output: Tensor
    ) -> list[Tensor]:
        # """VJP rule: reverse the permutation."""
        # Create inverse permutation for negative indices
        inv_axes = [0] * len(self.axes)
        for i, axis in enumerate(self.axes):
            # Convert negative axis to positive index for inverse mapping
            pos_axis = axis + len(self.axes)
            inv_axes[pos_axis] = i

        # Convert back to negative indices
        inv_axes_negative = [-len(self.axes) + ax for ax in inv_axes]
        return [permute_batch_dims(cotangent, tuple(inv_axes_negative))]

    def jvp_rule(
        self, primals: list[Tensor], tangents: list[Tensor], output: Tensor
    ) -> Tensor:
        """JVP rule: apply same permutation to tangent."""
        return permute_batch_dims(tangents[0], self.axes)


def permute_batch_dims(input_tensor: Tensor, axes: tuple[int, ...]) -> Tensor:
    """Permute (reorder) the batch dimensions of an tensor.

    This operation reorders the batch_dims of an Tensor according to the given axes,
    similar to how regular permute works on shape dimensions. The shape dimensions
    remain unchanged.

    Parameters
    ----------
        input_tensor: Input tensor with batch dimensions to permute
        axes: Tuple specifying the new order of batch dimensions.
              All indices should be negative and form a permutation.

    Returns
    -------
        Tensor with batch dimensions reordered according to axes

    Examples
    --------
        >>> import nabla as nb
        >>> # Tensor with batch_dims=(2, 3, 4) and shape=(5, 6)
        >>> x = nb.ones((5, 6))
        >>> x.batch_dims = (2, 3, 4)  # Simulated for example
        >>> y = permute_batch_dims(x, (-1, -3, -2))  # Reorder as (4, 2, 3)
        >>> # Result has batch_dims=(4, 2, 3) and shape=(5, 6)
    """
    if len(axes) <= 1:
        return input_tensor  # No permutation needed for single axis or empty

    # Convert to negative indices for consistency with batch dimension handling
    axes = tuple(-len(input_tensor.batch_dims) + ax if ax >= 0 else ax for ax in axes)

    # Handle case where fewer axes are provided - prepend missing axes to front
    if len(axes) < len(input_tensor.batch_dims):
        axes_new = []
        for i in range(-len(input_tensor.batch_dims), -len(axes)):
            axes_new.append(i)
        axes = tuple(axes_new) + axes

    op = PermuteBatchDimsOp(axes)
    return op.forward(input_tensor)


def move_axis_to_front(input_tensor: Tensor, axis: int) -> Tensor:
    """Move specified axis to the front (position 0), shifting others right.

    Parameters
    ----------
        input_tensor: Input tensor
        axis: Axis to move to front

    Returns
    -------
        Tensor with specified axis moved to front

    Examples
    --------
        >>> x = nb.ones((2, 3, 4))  # shape (2, 3, 4)
        >>> y = move_axis_to_front(x, 2)  # shape (4, 2, 3)
        >>> # axis 2 moved to front, others shifted: [2, 0, 1]
    """
    ndim = len(input_tensor.shape)

    # Normalize negative axis
    if axis < 0:
        axis = ndim + axis

    if axis < 0 or axis >= ndim:
        raise ValueError(f"Axis {axis} out of bounds for tensor of dimension {ndim}")

    # Generate permutation: [axis, 0, 1, ..., axis-1, axis+1, ..., ndim-1]
    axes = [axis] + [i for i in range(ndim) if i != axis]

    return permute(input_tensor, tuple(axes))


def move_axis_to_back(input_tensor: Tensor, axis: int) -> Tensor:
    """Move specified axis to the back (last position), shifting others left.

    Parameters
    ----------
        input_tensor: Input tensor
        axis: Axis to move to back

    Returns
    -------
        Tensor with specified axis moved to back

    Examples
    --------
        >>> x = nb.ones((2, 3, 4))  # shape (2, 3, 4)
        >>> y = move_axis_to_back(x, 0)  # shape (3, 4, 2)
        >>> # axis 0 moved to back, others shifted: [1, 2, 0]
    """
    ndim = len(input_tensor.shape)

    # Normalize negative axis
    if axis < 0:
        axis = ndim + axis

    if axis < 0 or axis >= ndim:
        raise ValueError(f"Axis {axis} out of bounds for tensor of dimension {ndim}")

    # Generate permutation: [0, 1, ..., axis-1, axis+1, ..., ndim-1, axis]
    axes = [i for i in range(ndim) if i != axis] + [axis]

    return permute(input_tensor, tuple(axes))


def move_axis_from_front(input_tensor: Tensor, target_axis: int) -> Tensor:
    """Move front axis (position 0) to specified target position.

    Parameters
    ----------
        input_tensor: Input tensor (assumes front axis is the one to move)
        target_axis: Target position for the front axis

    Returns
    -------
        Tensor with front axis moved to target position

    Examples
    --------
        >>> x = nb.ones((4, 2, 3))  # front axis has size 4
        >>> y = move_axis_from_front(x, 2)  # shape (2, 3, 4)
        >>> # front axis moved to position 2: [1, 2, 0]
    """
    ndim = len(input_tensor.shape)

    # Normalize negative axis
    if target_axis < 0:
        target_axis = ndim + target_axis

    if target_axis < 0 or target_axis >= ndim:
        raise ValueError(
            f"Target axis {target_axis} out of bounds for tensor of dimension {ndim}"
        )

    if target_axis == 0:
        return input_tensor  # Already at front

    # Generate permutation to move front to target_axis
    # [1, 2, ..., target_axis, 0, target_axis+1, ..., ndim-1]
    axes = list(range(1, target_axis + 1)) + [0] + list(range(target_axis + 1, ndim))

    return permute(input_tensor, tuple(axes))


def move_axis_from_back(input_tensor: Tensor, target_axis: int) -> Tensor:
    """Move back axis (last position) to specified target position.

    Parameters
    ----------
        input_tensor: Input tensor (assumes back axis is the one to move)
        target_axis: Target position for the back axis

    Returns
    -------
        Tensor with back axis moved to target position

    Examples
    --------
        >>> x = nb.ones((4, 2, 3))  # back axis has size 3
        >>> y = move_axis_from_back(x, 1)  # shape (2, 4, 3)
        >>> # back axis moved to position 1: [0, 2, 1]
    """
    ndim = len(input_tensor.shape)

    # Normalize negative axis
    if target_axis < 0:
        target_axis = ndim + target_axis

    if target_axis < 0 or target_axis >= ndim:
        raise ValueError(
            f"Target axis {target_axis} out of bounds for tensor of dimension {ndim}"
        )

    if target_axis == ndim - 1:
        return input_tensor  # Already at back

    # Generate permutation to move back to target_axis
    axes = list(range(0, target_axis)) + [ndim - 1] + list(range(target_axis, ndim - 1))

    return permute(input_tensor, tuple(axes))


def move_axis_to_front_of_batch_dims(input_tensor: Tensor, axis: int) -> Tensor:
    """Move specified batch dimension to the front (position 0), shifting others right.

    Parameters
    ----------
        input_tensor: Input tensor with batch dimensions
        axis: Batch dimension to move to front (negative index)

    Returns
    -------
        Tensor with specified batch dimension moved to front

    Examples
    --------
        >>> x = nb.ones((2, 3, 4))  # shape (2, 3, 4)
        >>> x.batch_dims = (1, 0)  # Simulated for example
        >>> y = move_axis_to_fron_of_batch_dims(x, -1)  # Move last batch dim to front
        >>> # Result has batch_dims=(0, 1) and shape=(2, 3, 4)
    """
    ndim = len(input_tensor.batch_dims)

    # Normalize negative axis
    if axis >= 0:
        axis = -len(input_tensor.batch_dims) + axis

    if axis < -len(input_tensor.batch_dims) or axis >= 0:
        raise ValueError(
            f"Axis {axis} out of bounds for batch_dims of dimension {ndim}"
        )

    # Generate permutation: [axis, 0, 1, ..., axis-1, axis+1, ..., ndim-1]
    axes = [axis] + [i for i in range(-len(input_tensor.batch_dims), 0) if i != axis]

    return permute_batch_dims(input_tensor, tuple(axes))


def move_axis_from_front_of_batch_dims(input_tensor: Tensor, target_axis: int) -> Tensor:
    """Move front batch dimension (position 0) to specified target position.

    Parameters
    ----------
        input_tensor: Input tensor with batch dimensions (assumes front batch dim is the one to move)
        target_axis: Target position for the front batch dimension (negative index)

    Returns
    -------
        Tensor with front batch dimension moved to target position

    Examples
    --------
        >>> x = nb.ones((4, 2, 3))  # shape (4, 2, 3)
        >>> x.batch_dims = (0, 1)  # Simulated for example
        >>> y = move_axis_from_front_of_batch_dims(x, -1)  # Move front batch dim to last position
        >>> # Result has batch_dims=(1, 0) and shape=(4, 2, 3)
    """
    ndim = len(input_tensor.batch_dims)

    # Normalize negative axis
    if target_axis >= 0:
        target_axis = -len(input_tensor.batch_dims) + target_axis

    if target_axis < -len(input_tensor.batch_dims) or target_axis >= 0:
        raise ValueError(
            f"Target axis {target_axis} out of bounds for batch_dims of dimension {ndim}"
        )

    if target_axis == 0:
        return input_tensor  # Already at front

    # Generate permutation to move front to target_axis
    axes = (
        list(range(-len(input_tensor.batch_dims) + 1, target_axis + 1))
        + [0]
        + list(range(target_axis + 1, 0))
    )

    return permute_batch_dims(input_tensor, tuple(axes))


class ReshapeOp(ViewOperation):
    """Reshape operation."""

    def __init__(self, arg_shape: Shape, target_shape: Shape):
        super().__init__(f"reshape[new_sizes={target_shape}]")
        self.arg_shape = arg_shape
        self.target_shape = target_shape

    def compute_output_shape(self, *input_shapes: tuple) -> tuple:
        """Compatible signature."""
        if len(input_shapes) != 1:
            raise ValueError(
                f"Reshape operation requires 1 input shape, got {len(input_shapes)}"
            )
        return self.target_shape

    def forward(self, *args: Tensor) -> Tensor:
        """Override forward to validate size compatibility with compatible signature."""
        if len(args) != 1:
            raise ValueError(f"Reshape operation requires 1 argument, got {len(args)}")
        arg = args[0]

        old_size = np.prod(arg.shape) if arg.shape else 1
        new_size = np.prod(self.target_shape) if self.target_shape else 1
        if old_size != new_size:
            raise ValueError(
                f"Cannot reshape tensor of size {old_size} to shape {self.target_shape} of size {new_size}"
            )

        return super().forward(arg)

    def maxpr(self, args: list[TensorValue], output: Tensor) -> None:
        output.tensor_value = ops.reshape(
            args[0], output.batch_dims + self.target_shape
        )

    def eagerxpr(self, args: list[Tensor], output: Tensor) -> None:
        np_result = np.reshape(
            args[0].to_numpy(), output.batch_dims + self.target_shape
        )
        output.impl_(np_result)

    def vjp_rule(
        self, primals: list[Tensor], cotangent: Tensor, output: Tensor
    ) -> list[Tensor]:
        return [reshape(cotangent, self.arg_shape)]

    def jvp_rule(
        self, primals: list[Tensor], tangents: list[Tensor], output: Tensor
    ) -> Tensor:
        return reshape(tangents[0], self.target_shape)


def reshape(arg: Tensor, shape: Shape) -> Tensor:
    """Reshape tensor to given shape."""
    # Handle -1 dimension inference
    if -1 in shape:
        # Compute the inferred dimension
        total_size = np.prod(arg.shape) if arg.shape else 1
        known_size = 1
        unknown_idx = -1

        for i, dim in enumerate(shape):
            if dim == -1:
                if unknown_idx != -1:
                    raise ValueError("Can only specify one unknown dimension with -1")
                unknown_idx = i
            else:
                known_size *= dim

        if unknown_idx == -1:
            # No -1 found, use shape as is
            target_shape = shape
        else:
            # Calculate the unknown dimension
            if known_size == 0:
                raise ValueError(
                    "Cannot infer shape when known dimensions have zero size"
                )
            if total_size % known_size != 0:
                raise ValueError(
                    f"Cannot reshape tensor of size {total_size} to shape {shape}"
                )

            inferred_dim = total_size // known_size
            target_shape = tuple(
                int(inferred_dim if dim == -1 else dim) for dim in shape
            )
    else:
        target_shape = tuple(int(dim) for dim in shape)

    op = ReshapeOp(arg.shape, target_shape)
    return op.forward(arg)


class BroadcastToOp(ViewOperation):
    """Broadcast tensor to target shape."""

    def __init__(self, target_shape: Shape):
        super().__init__(f"broadcast[shape={target_shape}]")
        self.target_shape = target_shape

    def compute_output_shape(self, *input_shapes: tuple) -> tuple:
        """Compatible signature."""
        if len(input_shapes) != 1:
            raise ValueError(
                f"Broadcast operation requires 1 input shape, got {len(input_shapes)}"
            )
        return self.target_shape

    def forward(self, *args: Tensor) -> Tensor:
        """Override forward to handle case where no broadcasting needed with compatible signature."""
        if len(args) != 1:
            raise ValueError(
                f"Broadcast operation requires 1 argument, got {len(args)}"
            )
        arg = args[0]
        if arg.shape == self.target_shape:
            return arg
        return super().forward(*args)

    @staticmethod
    def get_broadcasted_axes(input_shape: Shape, target_shape: Shape) -> list[int]:
        """Get axes that were broadcasted (for VJP)."""
        if len(input_shape) > len(target_shape):
            raise ValueError(
                f"Input shape {input_shape} cannot be broadcast to {target_shape}"
            )

        broadcasted_axes = []
        padded_input = (1,) * (len(target_shape) - len(input_shape)) + input_shape

        for i in range(len(target_shape)):
            if padded_input[i] == 1 and target_shape[i] > 1:
                # Return negative index to reference from the right side
                # This ensures we sum over the correct dimension
                broadcasted_axes.append(i - len(target_shape))
            elif padded_input[i] != target_shape[i] and padded_input[i] != 1:
                raise ValueError(f"Cannot broadcast {input_shape} to {target_shape}")

        return broadcasted_axes

    def maxpr(self, args: list[TensorValue], output: Tensor) -> None:
        output.tensor_value = ops.broadcast_to(
            args[0], output.batch_dims + self.target_shape
        )

    def eagerxpr(self, args: list[Tensor], output: Tensor) -> None:
        np_result = np.broadcast_to(
            args[0].to_numpy(), shape=output.batch_dims + self.target_shape
        )
        output.impl_(np_result)

    def vjp_rule(
        self, primals: list[Tensor], cotangent: Tensor, output: Tensor
    ) -> list[Tensor]:
        broadcasted_axes = self.get_broadcasted_axes(
            primals[0].shape, self.target_shape
        )
        from .reduce import sum as sum_op  # Renamed to avoid shadowing built-in

        return [sum_op(cotangent, axes=broadcasted_axes, keep_dims=True)]

    def jvp_rule(
        self, primals: list[Tensor], tangents: list[Tensor], output: Tensor
    ) -> Tensor:
        return broadcast_to(tangents[0], self.target_shape)


def broadcast_to(arg: Tensor, shape: Shape) -> Tensor:
    """Broadcast tensor to target shape."""
    if arg.shape == shape:
        return arg
    for _ in range(len(shape) - len(arg.shape)):
        arg = unsqueeze(arg, [0])
    op = BroadcastToOp(shape)
    return op.forward(arg)


class BroadcastBatchDimsOp(ViewOperation):
    """Broadcast tensor to target batch_dims."""

    def __init__(self, target_batch_dims: Shape):
        super().__init__(f"broadcast_batch_dims[shape={target_batch_dims}]")
        self.target_batch_dims = target_batch_dims

    def compute_output_batch_dims(self, *input_batch_dimss: tuple) -> tuple:
        """Compatible signature."""
        if len(input_batch_dimss) != 1:
            raise ValueError(
                f"Broadcast operation requires 1 input batch_dims, got {len(input_batch_dimss)}"
            )
        return self.target_batch_dims

    def forward(self, *args: Tensor) -> Tensor:
        """Override forward to handle case where no broadcasting needed with compatible signature."""
        if len(args) != 1:
            raise ValueError(
                f"Broadcast operation requires 1 argument, got {len(args)}"
            )
        arg = args[0]
        if arg.batch_dims == self.target_batch_dims:
            return arg
        return super().forward(*args)

    @staticmethod
    def get_broadcasted_axes(
        input_batch_dims: Shape, target_batch_dims: Shape
    ) -> list[int]:
        """Get axes that were broadcasted (for VJP)."""
        if len(input_batch_dims) > len(target_batch_dims):
            raise ValueError(
                f"Input batch_dims {input_batch_dims} cannot be broadcast to {target_batch_dims}"
            )

        broadcasted_axes = []
        padded_input = (1,) * (
            len(target_batch_dims) - len(input_batch_dims)
        ) + input_batch_dims

        for i in range(len(target_batch_dims)):
            if padded_input[i] == 1 and i < len(target_batch_dims) - len(
                input_batch_dims
            ):
                # This dimension was added by padding (broadcasted from non-existent to size 1 or more)
                broadcasted_axes.append(i - len(target_batch_dims))
            elif padded_input[i] == 1 and target_batch_dims[i] > 1:
                # This dimension was broadcasted from size 1 to larger size
                broadcasted_axes.append(i - len(target_batch_dims))
            elif padded_input[i] != target_batch_dims[i] and padded_input[i] != 1:
                raise ValueError(
                    f"Cannot broadcast {input_batch_dims} to {target_batch_dims}"
                )

        return broadcasted_axes

    def maxpr(self, args: list[TensorValue], output: Tensor) -> None:
        output.tensor_value = ops.broadcast_to(
            args[0], self.target_batch_dims + output.shape
        )

    def eagerxpr(self, args: list[Tensor], output: Tensor) -> None:
        np_result = np.broadcast_to(
            args[0].to_numpy(), shape=self.target_batch_dims + output.shape
        )
        output.impl_(np_result)

    def vjp_rule(
        self, primals: list[Tensor], cotangent: Tensor, output: Tensor
    ) -> list[Tensor]:
        from .reduce import sum_batch_dims

        broadcasted_axes = self.get_broadcasted_axes(
            primals[0].batch_dims, output.batch_dims
        )
        return [sum_batch_dims(cotangent, axes=broadcasted_axes, keep_dims=True)]

    def jvp_rule(
        self, primals: list[Tensor], tangents: list[Tensor], output: Tensor
    ) -> Tensor:
        return broadcast_batch_dims(tangents[0], self.target_batch_dims)


def broadcast_batch_dims(arg: Tensor, batch_dims: Shape) -> Tensor:
    """Broadcast tensor to target batch_dims."""
    if arg.batch_dims == batch_dims:
        return arg

    for _ in range(len(batch_dims) - len(arg.batch_dims)):
        arg = unsqueeze_batch_dims(arg, [0])

    op = BroadcastBatchDimsOp(batch_dims)
    return op.forward(arg)


class SqueezeOp(ViewOperation):
    """Squeeze operation to remove dimensions of size 1."""

    def __init__(self, axes: list[int] | None = None):
        super().__init__(f"squeeze[axes={axes}]")
        self.axes = sorted(axes) if axes is not None else []

    def compute_output_shape(self, *input_shapes: tuple) -> tuple:
        """Compatible signature."""
        if len(input_shapes) != 1:
            raise ValueError(
                f"Squeeze operation requires 1 input shape, got {len(input_shapes)}"
            )
        input_shape = input_shapes[0]

        new_shape = list(input_shape)
        for ax in self.axes:
            if ax < -len(new_shape) or ax >= len(new_shape):
                raise ValueError(f"Axis {ax} is out of bounds for squeeze operation")
            if input_shape[ax] == 1:
                new_shape[ax] = None
            else:
                raise ValueError(
                    f"Cannot squeeze axis {ax} of size {input_shape[ax]} (must be 1)"
                )

        new_shape = [dim for dim in new_shape if dim is not None]
        return tuple(new_shape)

    def forward(self, *args: Tensor) -> Tensor:
        """Override forward to handle case where no squeezing needed with compatible signature."""
        if len(args) != 1:
            raise ValueError(f"Squeeze operation requires 1 argument, got {len(args)}")
        return super().forward(*args)

    def maxpr(self, args: list[TensorValue], output: Tensor) -> None:
        res = args[0]
        # Use self.axes directly since it's already normalized to a list in __init__
        for ax in self.axes:
            res = ops.squeeze(res, ax)
        output.tensor_value = res

    def eagerxpr(self, args: list[Tensor], output: Tensor) -> None:
        axis = tuple(self.axes) if self.axes else None
        np_result = np.squeeze(args[0].to_numpy(), axis=axis)
        output.impl_(np_result)

    def vjp_rule(
        self, _primals: list[Tensor], cotangent: Tensor, _output: Tensor
    ) -> list[Tensor]:
        return [unsqueeze(cotangent, self.axes)]

    def jvp_rule(
        self, _primals: list[Tensor], tangents: list[Tensor], _output: Tensor
    ) -> Tensor:
        return squeeze(tangents[0], self.axes)


def squeeze(arg: Tensor, axes: list[int] | None = None) -> Tensor:
    """Squeeze tensor by removing dimensions of size 1."""
    if axes is None:
        return arg
    axes = [ax if ax < 0 else -len(arg.shape) + ax for ax in axes]

    op = SqueezeOp(axes)
    res = op.forward(arg)

    return res


class UnsqueezeOp(ViewOperation):
    """Unsqueeze operation to add dimensions of size 1."""

    def __init__(self, axes: list[int] | None = None):
        super().__init__(f"unsqueeze[axes={axes}]")
        self.axes = sorted(axes) if axes is not None else []

    def compute_output_shape(self, *input_shapes: tuple) -> tuple:
        """Compatible signature."""
        if len(input_shapes) != 1:
            raise ValueError(
                f"Unsqueeze operation requires 1 input shape, got {len(input_shapes)}"
            )
        input_shape = input_shapes[0]

        new_shape = list(input_shape)
        for ax in self.axes:
            if ax < -len(new_shape) - 1:
                raise ValueError(f"Axis {ax} is out of bounds for unsqueeze operation")
            if ax + 1 <= -1:
                new_shape.insert(ax + 1, 1)
            else:
                new_shape.append(1)

        return tuple(new_shape)

    def forward(self, *args: Tensor) -> Tensor:
        """Override forward to handle case where no unsqueezing needed with compatible signature."""
        if len(args) != 1:
            raise ValueError(
                f"Unsqueeze operation requires 1 argument, got {len(args)}"
            )
        return super().forward(*args)

    def maxpr(self, args: list[TensorValue], output: Tensor) -> None:
        res_value = args[0]
        for ax in self.axes:
            res_value = ops.unsqueeze(res_value, ax)
        output.tensor_value = res_value

    def eagerxpr(self, args: list[Tensor], output: Tensor) -> None:
        np_result = np.expand_dims(args[0].to_numpy(), axis=self.axes)
        output.impl_(np_result)

    def vjp_rule(
        self, primals: list[Tensor], cotangent: Tensor, output: Tensor
    ) -> list[Tensor]:
        return [squeeze(cotangent, self.axes)]

    def jvp_rule(
        self, primals: list[Tensor], tangents: list[Tensor], output: Tensor
    ) -> Tensor:
        return unsqueeze(tangents[0], self.axes)


def unsqueeze(arg: Tensor, axes: list[int] | None = None) -> Tensor:
    """Unsqueeze tensor by adding dimensions of size 1."""
    if axes is None:
        return arg

    axes = [ax if ax < 0 else -len(arg.shape) - 1 + ax for ax in axes]
    op = UnsqueezeOp(axes)
    return op.forward(arg)


class ShallowCopyOp(ViewOperation):
    """Copy operation to create a new tensor with the same data."""

    def __init__(self, arg: Tensor):
        # if not arg.name and arg._impl and arg.shape == () and arg.batch_dims == ():
        #     name = arg.to_numpy().__repr__()  # Use numpy repr for empty tensors
        # else:
        name = "shallow_copy"

        super().__init__(name)

    def compute_output_shape(self, *input_shapes: tuple) -> tuple:
        """Compatible signature."""
        if len(input_shapes) != 1:
            raise ValueError(
                f"Copy operation requires 1 input shape, got {len(input_shapes)}"
            )
        return input_shapes[0]

    def maxpr(self, args: list[TensorValue], output: Tensor) -> None:
        output.tensor_value = args[0]

    def eagerxpr(self, args: list[Tensor], output: Tensor) -> None:
        output.impl_(args[0]._impl)

    def vjp_rule(
        self, primals: list[Tensor], cotangent: Tensor, output: Tensor
    ) -> list[Tensor]:
        return [cotangent]

    def jvp_rule(
        self, primals: list[Tensor], tangents: list[Tensor], output: Tensor
    ) -> Tensor:
        return tangents[0]


def shallow_copy(arg: Tensor) -> Tensor:
    """Create a shallow copy of the tensor."""
    op = ShallowCopyOp(arg)
    return op.forward(arg)


class ConcatenateOp(Operation):
    """Concatenate operation to join tensors along an existing axis."""

    def __init__(self, axis: int = 0):
        super().__init__(f"concatenate[axis={axis}]")
        self.axis = axis

    def compute_output_shape(self, *input_shapes: tuple) -> tuple:
        """Compute output shape for concatenate operation."""
        if len(input_shapes) == 0:
            raise ValueError("Concatenate operation requires at least 1 input")

        # All input shapes must be the same except along the concatenation axis
        first_shape = input_shapes[0]
        if not first_shape:
            raise ValueError("Cannot concatenate empty shapes")

        # Normalize axis
        axis = self.axis if self.axis >= 0 else len(first_shape) + self.axis
        if axis < 0 or axis >= len(first_shape):
            raise ValueError(
                f"Axis {self.axis} is out of bounds for tensor with {len(first_shape)} dimensions"
            )

        # Check that all shapes are compatible
        total_size_along_axis = 0
        for i, shape in enumerate(input_shapes):
            if len(shape) != len(first_shape):
                raise ValueError(
                    f"All inputs must have the same number of dimensions for concatenate operation. "
                    f"Input 0 has {len(first_shape)} dimensions, input {i} has {len(shape)} dimensions"
                )

            for j, (dim1, dim2) in enumerate(zip(first_shape, shape, strict=False)):
                if j != axis and dim1 != dim2:
                    raise ValueError(
                        f"All inputs must have the same shape except along axis {axis}. "
                        f"Input 0 has shape {first_shape}, input {i} has shape {shape}"
                    )

            total_size_along_axis += shape[axis]

        # Compute output shape
        output_shape = list(first_shape)
        output_shape[axis] = total_size_along_axis
        return tuple(output_shape)

    def maxpr(self, args: list[TensorValue], output: Tensor) -> None:
        """MAX graph implementation using ops.concat."""
        # Normalize axis for MAX operations, considering batch_dims
        # full_output_shape = output.batch_dims + output.shape  # TODO: Use if needed
        axis = self.axis if self.axis >= 0 else len(output.shape) + self.axis

        # Adjust axis to account for batch_dims in the actual tensor
        axis_in_tensor = axis + len(output.batch_dims)
        output.tensor_value = ops.concat(args, axis=axis_in_tensor)

    def eagerxpr(self, args: list[Tensor], output: Tensor) -> None:
        """Eager execution using NumPy concatenate."""
        import numpy as np

        numpy_tensors = [arg.to_numpy() for arg in args]
        # Normalize axis for NumPy operations, considering batch_dims
        axis = self.axis if self.axis >= 0 else len(output.shape) + self.axis

        # Adjust axis to account for batch_dims in the actual tensor
        axis_in_tensor = axis + len(output.batch_dims)
        result = np.concatenate(numpy_tensors, axis=axis_in_tensor)
        output.impl_(result)

    def vjp_rule(
        self, primals: list[Tensor], cotangent: Tensor, output: Tensor
    ) -> list[Tensor]:
        """Vector-Jacobian product rule for concatenate operation.

        The VJP of concatenate is slicing the cotangent back into pieces.
        """
        # Normalize axis
        axis = self.axis if self.axis >= 0 else len(cotangent.shape) + self.axis

        # Split the cotangent along the concatenated axis
        result = []
        start_idx = 0

        for primal in primals:
            size_along_axis = primal.shape[axis]
            end_idx = start_idx + size_along_axis

            # Create slice that selects this input's portion along the concatenated axis
            slices = [slice(None)] * len(cotangent.shape)
            slices[axis] = slice(start_idx, end_idx)

            # Slice the cotangent
            sliced = tensor_slice(cotangent, slices)
            result.append(sliced)

            start_idx = end_idx

        return result

    def jvp_rule(
        self, primals: list[Tensor], tangents: list[Tensor], output: Tensor
    ) -> Tensor:
        """Jacobian-vector product rule for concatenate operation.

        The JVP of concatenate is concatenating the tangents along the same axis.
        """
        # Use the ConcatenateOp directly to avoid circular import
        op = ConcatenateOp(axis=self.axis)
        return op.forward(*tangents)

    def forward(self, *args: Tensor) -> Tensor:
        """Forward pass for concatenate operation with multiple inputs."""
        if len(args) == 0:
            raise ValueError("Concatenate operation requires at least 1 argument")

        # Move tensors to best device
        from .operation import move_to_best_device

        args = move_to_best_device(*args)

        # Validate inputs have compatible properties
        first_arg = args[0]
        for _i, arg in enumerate(args[1:], 1):
            if arg.dtype != first_arg.dtype:
                raise ValueError(
                    f"All inputs must have the same dtype. Got {arg.dtype} vs {first_arg.dtype}"
                )
            if arg.logical_device != first_arg.logical_device:
                raise ValueError(
                    f"All inputs must be on the same device. Got {arg.logical_device} vs {first_arg.logical_device}"
                )

        # Compute output properties
        input_shapes = [arg.shape for arg in args]
        output_shape = self.compute_output_shape(*input_shapes)

        # All inputs should have the same batch_dims
        output_batch_dims = first_arg.batch_dims
        for i, arg in enumerate(args[1:], 1):
            if arg.batch_dims != output_batch_dims:
                raise ValueError(
                    f"All inputs must have the same batch_dims for concatenate operation. "
                    f"Input 0 has batch_dims {output_batch_dims}, input {i} has batch_dims {arg.batch_dims}"
                )

        # Create result tensor
        res = Tensor(
            shape=output_shape,
            dtype=first_arg.dtype,
            device=first_arg.logical_device,
            materialize=False,
            name=self.name,
            batch_dims=output_batch_dims,
        )

        # Set up computation
        res.set_maxpr(self.maxpr)
        res.add_arguments(*args)
        res.vjp_rule = self.vjp_rule
        res.jvp_rule = self.jvp_rule

        # Execute eager computation if needed
        if not res.stage_realization:
            self.eagerxpr(list(args), res)

        res.creator_op = self
        return res


def concatenate(args: list[Tensor], axis: int = 0) -> Tensor:
    """Concatenate tensors along an existing axis.

    Parameters
    ----------
        args: List of tensors to concatenate
        axis: Axis along which to concatenate tensors (default: 0)

    Returns
    -------
        Concatenated tensor
    """
    if not args:
        raise ValueError("Concatenate operation requires at least one tensor")

    op = ConcatenateOp(axis)
    return op.forward(*args)


class TensorSliceOp(ViewOperation):
    """Tensor slicing operation."""

    def __init__(self, slices: list[slice], squeeze_axes: list[int] | None = None):
        # Store original slices for reference
        self.original_slices = slices.copy()

        # Check if we have negative steps - if so, we'll need special handling
        self.has_negative_steps = any(s.step is not None and s.step < 0 for s in slices)

        # Convert slices to a more manageable format
        slice_strs = []
        for s in slices:
            start = s.start if s.start is not None else ""
            stop = s.stop if s.stop is not None else ""
            step = s.step if s.step is not None else ""
            if step and step != 1:
                slice_strs.append(f"{start}:{stop}:{step}")
            else:
                slice_strs.append(f"{start}:{stop}")

        squeeze_info = f"_squeeze{squeeze_axes}" if squeeze_axes else ""
        super().__init__(f"tensor_slice[{','.join(slice_strs)}]{squeeze_info}")
        self.slices = slices
        self.squeeze_axes = squeeze_axes or []

    def compute_output_shape(self, *input_shapes: tuple) -> tuple:
        """Compute output shape for tensor slice operation."""
        if len(input_shapes) != 1:
            raise ValueError(
                f"Tensor slice operation requires 1 input shape, got {len(input_shapes)}"
            )

        input_shape = input_shapes[0]
        output_shape = []

        if len(self.slices) > len(input_shape):
            raise IndexError(
                f"too many indices for tensor: tensor is {len(input_shape)}-dimensional, but {len(self.slices)} were indexed"
            )

        # Process each dimension
        for i, dim_size in enumerate(input_shape):
            if i < len(self.slices):
                s = self.slices[i]
                start = s.start if s.start is not None else 0
                stop = s.stop if s.stop is not None else dim_size
                step = s.step if s.step is not None else 1

                # Handle negative indices
                if start < 0:
                    start = max(0, dim_size + start)
                if stop < 0:
                    stop = max(0, dim_size + stop)

                # Clamp to valid range
                start = max(0, min(start, dim_size))
                stop = max(start, min(stop, dim_size))

                # Calculate output size for this dimension
                if step > 0:
                    output_size = max(0, (stop - start + step - 1) // step)
                elif step < 0:
                    # Handle negative step - reverse direction
                    # For negative step, we need start > stop (conceptually)
                    # But we need to handle the actual range calculation
                    if start >= stop:
                        # For negative step with start >= stop, we go from start down to stop+1
                        output_size = max(0, (start - stop + (-step) - 1) // (-step))
                    else:
                        # Invalid range for negative step
                        output_size = 0
                else:
                    raise ValueError("Step cannot be zero")

                # Skip this dimension if it should be squeezed (JAX-compatible behavior)
                if i not in self.squeeze_axes:
                    output_shape.append(output_size)
            else:
                # No slice for this dimension, keep original size
                output_shape.append(dim_size)

        return tuple(output_shape)

    def maxpr(self, args: list[TensorValue], output: Tensor) -> None:
        """MAX graph implementation using ops.slice_tensor."""
        input_tensor = args[0]
        # Check for negative steps - not supported in JIT mode yet
        if self.has_negative_steps:
            raise NotImplementedError(
                "Negative step slicing (e.g., [::-1]) is not yet supported in JIT-compiled functions "
                "due to MAX engine limitations. Use eager execution instead, or avoid negative steps "
                "in JIT-compiled code."
            )

        # Build slice indices for MAX ops.slice_tensor
        slice_indices = []
        # Add full slices for batch dimensions
        for _ in range(len(output.batch_dims)):
            slice_indices.append(slice(None))
        # Add the user-provided slices
        slice_indices.extend(self.slices)

        # Pad with full slices up to the total rank of the input tensor.
        num_physical_dims = len(input_tensor.shape)
        while len(slice_indices) < num_physical_dims:
            slice_indices.append(slice(None))

        # Truncate if too long (can happen in weird vmap cases)
        slice_indices = slice_indices[:num_physical_dims]

        # Apply the slicing
        result = ops.slice_tensor(input_tensor, slice_indices)

        # Apply squeezing for JAX-compatible behavior
        if self.squeeze_axes:
            # Adjust squeeze axes to account for batch dimensions
            squeeze_axes_adjusted = [
                ax + len(output.batch_dims) for ax in self.squeeze_axes
            ]
            for ax in sorted(
                squeeze_axes_adjusted, reverse=True
            ):  # Squeeze in reverse order
                result = ops.squeeze(result, ax)

        output.tensor_value = result

    def eagerxpr(self, args: list[Tensor], output: Tensor) -> None:
        """Eager execution using NumPy slicing."""
        input_tensor = args[0].to_numpy()

        # Build numpy slice tuple
        # Need to account for batch_dims - slicing only applies to shape dimensions
        numpy_slices = []

        # Add full slices for batch dimensions
        for _ in range(len(args[0].batch_dims)):
            numpy_slices.append(slice(None))

        # Add the actual slices for shape dimensions
        for i in range(len(args[0].shape)):
            if i < len(self.slices):
                numpy_slices.append(self.slices[i])
            else:
                numpy_slices.append(slice(None))  # Full slice for remaining dimensions

        result = input_tensor[tuple(numpy_slices)]

        # Apply squeezing for JAX-compatible behavior
        if self.squeeze_axes:
            # Adjust squeeze axes to account for batch dimensions
            squeeze_axes_adjusted = [
                ax + len(args[0].batch_dims) for ax in self.squeeze_axes
            ]
            result = np.squeeze(result, axis=tuple(squeeze_axes_adjusted))

        output.impl_(result)

    def vjp_rule(
        self, primals: list[Tensor], cotangent: Tensor, output: Tensor
    ) -> list[Tensor]:
        """Vector-Jacobian product rule for tensor slice."""
        # If we squeezed dimensions, we need to unsqueeze the cotangent first
        if self.squeeze_axes:
            from ..ops.view import unsqueeze

            # Unsqueeze in the positions that were squeezed
            unsqueeze_axes = self.squeeze_axes.copy()
            cotangent_unsqueezed = unsqueeze(cotangent, unsqueeze_axes)
        else:
            cotangent_unsqueezed = cotangent

        return [pad(cotangent_unsqueezed, self.slices, primals[0].shape)]

    def jvp_rule(
        self, primals: list[Tensor], tangents: list[Tensor], output: Tensor
    ) -> Tensor:
        """Jacobian-vector product rule for tensor slice."""
        # Apply the same slicing and squeezing to tangents
        op = TensorSliceOp(self.slices, self.squeeze_axes)
        return op.forward(tangents[0])


def tensor_slice(
    arg: Tensor, slices: list[slice], squeeze_axes: list[int] | None = None
) -> Tensor:
    """Slice an tensor along specified dimensions.

    Parameters
    ----------
        arg: Input tensor to slice
        slices: List of slice objects defining the slicing for each dimension
        squeeze_axes: List of axes that should be squeezed (for JAX compatibility)

    Returns
    -------
        Sliced tensor
    """
    op = TensorSliceOp(slices, squeeze_axes)
    return op.forward(arg)


def split(arg: Tensor, sizes: list[int], axis: int = 0) -> list[Tensor]:
    """Split an tensor into multiple sub-tensors along a specified axis.

    Parameters
    ----------
        arg: Input tensor to split
        sizes: List of sizes for each split along the specified axis
        axis: Axis along which to split the tensor (default: 0)
    Returns
    -------
        List of sub-tensors resulting from the split
    """
    if not sizes:
        raise ValueError("Sizes list must not be empty")

    if axis < 0:
        axis += len(arg.shape)

    if axis < 0 or axis >= len(arg.shape):
        raise ValueError(
            f"Axis {axis} is out of bounds for tensor with {len(arg.shape)} dimensions"
        )

    # Compute the total size along the specified axis
    total_size = sum(sizes)
    if total_size != arg.shape[axis]:
        raise ValueError(
            f"Total size {total_size} along axis {axis} does not match input shape {arg.shape[axis]}"
        )

    # Create slices for each split
    slices = []
    idx = 0
    for size in sizes:
        slices.append(slice(idx, idx + size))
        idx += size

    # Create the result tensors
    results = []
    for s in slices:
        slice_obj = [slice(None)] * len(arg.shape)  # Full slice for all dimensions
        slice_obj[axis] = s  # Set the slice for the specified axis
        results.append(tensor_slice(arg, slice_obj))

    return results


class PadOp(Operation):
    """Inverse slice operation - places a smaller tensor into a larger zero-filled tensor."""

    def __init__(self, slices: list[slice], target_shape: Shape):
        # Convert slices to string representation for name
        slice_strs = []
        for s in slices:
            start = s.start if s.start is not None else ""
            stop = s.stop if s.stop is not None else ""
            step = s.step if s.step is not None else ""
            if step and step != 1:
                slice_strs.append(f"{start}:{stop}:{step}")
            else:
                slice_strs.append(f"{start}:{stop}")

        super().__init__(f"pad[{','.join(slice_strs)}]")
        self.slices = slices
        self.target_shape = target_shape

    def compute_output_shape(self, *input_shapes: tuple) -> tuple:
        """Compute output shape for inverse slice operation."""
        if len(input_shapes) != 1:
            raise ValueError(
                f"Inverse slice operation requires 1 input shape, got {len(input_shapes)}"
            )

        # Validate that applying slices to target_shape would yield input_shape
        input_shape = input_shapes[0]

        # Simulate slicing target_shape with self.slices to verify consistency
        expected_shape = []
        for i, dim_size in enumerate(self.target_shape):
            if i < len(self.slices):
                s = self.slices[i]
                start = s.start if s.start is not None else 0
                stop = s.stop if s.stop is not None else dim_size
                step = s.step if s.step is not None else 1

                # Handle step sizes - now supported!
                # if step != 1:
                #     raise NotImplementedError(
                #         "Stepped slicing not yet supported in pad"
                #     )

                # Handle negative indices
                if start < 0:
                    start = max(0, dim_size + start)
                if stop < 0:
                    stop = max(0, dim_size + stop)

                # Clamp to valid range
                start = max(0, min(start, dim_size))
                stop = max(start, min(stop, dim_size))

                # Calculate output size for this dimension, accounting for step
                if step == 1:
                    output_size = stop - start
                else:
                    # For stepped slicing: number of elements = ceil((stop - start) / step)
                    output_size = (stop - start + step - 1) // step
                expected_shape.append(output_size)
            else:
                # No slice for this dimension, keep original size
                expected_shape.append(dim_size)

        expected_shape = tuple(expected_shape)
        if expected_shape != input_shape:
            raise ValueError(
                f"Slicing target_shape {self.target_shape} with {self.slices} "
                f"would produce shape {expected_shape}, but input has shape {input_shape}"
            )

        return self.target_shape

    def maxpr(self, args: list[TensorValue], output: Tensor) -> None:
        """MAX graph implementation using range->reshape->broadcast->slice->scatter approach."""
        import numpy as np

        input_tensor = args[0]

        # Step 1: Calculate total elements in output shape
        total_elements = int(np.prod(output.shape))

        # Step 2: Create flat index tensor using ops.range with int32 dtype
        flat_indices = ops.range(0, total_elements, 1, dtype=DType.int32)

        # Step 3: Reshape to output shape
        reshaped_indices = ops.reshape(flat_indices, output.shape)

        # Step 4: Broadcast to include batch dims if needed
        if output.batch_dims:
            # Need to broadcast to batch_dims + output.shape
            target_shape = list(output.batch_dims) + list(output.shape)
            broadcasted_indices = ops.broadcast_to(reshaped_indices, target_shape)
        else:
            broadcasted_indices = reshaped_indices

        # Step 5: Slice the index tensor using self.slices to get target indices
        slice_indices = []

        # Add full slices for batch dimensions
        for _ in range(len(output.batch_dims)):
            slice_indices.append(slice(None))

        # Add the actual slices for shape dimensions
        for s in self.slices:
            slice_indices.append(slice(s.start, s.stop, s.step))

        # Add full slices for any remaining dimensions
        for _ in range(len(self.slices), len(output.shape)):
            slice_indices.append(slice(None))

        # Slice to get the indices where input should go
        sliced_indices = ops.slice_tensor(broadcasted_indices, slice_indices)

        # Step 6: Flatten the sliced indices
        flattened_indices = ops.reshape(sliced_indices, [-1])

        # Step 7: Create flat zero tensor for scattering
        total_output_elements = int(
            np.prod(list(output.batch_dims) + list(output.shape))
        )
        from max.graph import DeviceRef

        zero_scalar = ops.constant(
            0.0, dtype=output.dtype, device=DeviceRef.from_device(output.logical_device)
        )
        flat_zeros = ops.broadcast_to(zero_scalar, [total_output_elements])

        # Step 8: Flatten input tensor
        input_flattened = ops.reshape(input_tensor, [-1])

        # Step 9: Use scatter to place input values at target indices
        scattered_flat = ops.scatter(
            flat_zeros, input_flattened, flattened_indices, axis=0
        )

        # Step 10: Reshape result back to target shape
        final_shape = list(output.batch_dims) + list(output.shape)
        output.tensor_value = ops.reshape(scattered_flat, final_shape)

    def eagerxpr(self, args: list[Tensor], output: Tensor) -> None:
        """Eager execution using NumPy."""
        small_tensor = args[0]

        # Create zero-filled target tensor
        target_shape = output.batch_dims + output.shape
        result_np = np.zeros(target_shape, dtype=small_tensor.to_numpy().dtype)

        # Build slice indices (accounting for batch_dims)
        slice_indices = []

        # Add full slices for batch dimensions
        for _ in range(len(output.batch_dims)):
            slice_indices.append(slice(None))

        # Add the actual slices for shape dimensions
        slice_indices.extend(self.slices)

        # Add full slices for any remaining dimensions
        for _i in range(len(self.slices), len(output.shape)):
            slice_indices.append(slice(None))

        # Place small tensor into the target location
        result_np[tuple(slice_indices)] = small_tensor.to_numpy()

        output.impl_(result_np)

    def vjp_rule(
        self, primals: list[Tensor], cotangent: Tensor, output: Tensor
    ) -> list[Tensor]:
        """VJP rule: slice the cotangent back to original size."""
        # The VJP of pad is just a regular slice!
        from nabla.ops.view import tensor_slice

        return [tensor_slice(cotangent, self.slices)]

    def jvp_rule(
        self, primals: list[Tensor], tangents: list[Tensor], output: Tensor
    ) -> Tensor:
        """JVP rule: apply pad to tangents."""
        return pad(tangents[0], self.slices, self.target_shape)

    def forward(self, *args: Tensor) -> Tensor:
        """Forward pass for inverse slice operation."""
        if len(args) != 1:
            raise ValueError(
                f"Inverse slice operation requires 1 argument, got {len(args)}"
            )

        input_tensor = args[0]

        # Compute output properties
        output_shape = self.compute_output_shape(input_tensor.shape)

        # Create result tensor
        res = Tensor(
            shape=output_shape,
            dtype=input_tensor.dtype,
            device=input_tensor.logical_device,
            materialize=False,
            name=self.name,
            batch_dims=input_tensor.batch_dims,
        )

        # Set up computation
        res.set_maxpr(self.maxpr)
        res.add_arguments(input_tensor)
        res.vjp_rule = self.vjp_rule
        res.jvp_rule = self.jvp_rule

        # Execute eager computation if needed
        if not res.stage_realization:
            self.eagerxpr([input_tensor], res)

        res.creator_op = self
        return res


def pad(arg: Tensor, slices: list[slice], target_shape: Shape) -> Tensor:
    """Place a smaller tensor into a larger zero-filled tensor at the location specified by slices.

    This is the inverse operation of tensor slicing - given slices, a small tensor, and target shape,
    it creates a larger tensor where the small tensor is placed at the sliced location
    and everything else is zero.

    Parameters
    ----------
        arg: Input tensor (the smaller tensor to be placed)
        slices: List of slice objects defining where to place the tensor
        target_shape: The shape of the output tensor

    Returns
    -------
        Larger tensor with input placed at sliced location, zeros elsewhere
    """
    op = PadOp(slices, target_shape)
    return op.forward(arg)


class SqueezeBatchDimsOp(ViewOperation):
    """Squeeze operation to remove batch dimensions of size 1."""

    def __init__(self, axes: list[int] | None = None):
        super().__init__(f"squeeze_batch_dims[axes={axes}]")
        self.axes = sorted(axes) if axes is not None else []

    def compute_output_shape(self, *input_shapes: tuple) -> tuple:
        """Shape stays the same for batch dimension operations."""
        if len(input_shapes) != 1:
            raise ValueError(
                f"Squeeze batch dims operation requires 1 input shape, got {len(input_shapes)}"
            )
        return input_shapes[0]

    def compute_output_batch_dims(self, *input_batch_dimss: tuple) -> tuple:
        """Compute output batch_dims for squeeze operation."""
        if len(input_batch_dimss) != 1:
            raise ValueError(
                f"Squeeze batch dims operation requires 1 input batch_dims, got {len(input_batch_dimss)}"
            )
        input_batch_dims = input_batch_dimss[0]

        new_batch_dims = list(input_batch_dims)
        for ax in self.axes:
            if ax < -len(new_batch_dims) or ax >= len(new_batch_dims):
                raise ValueError(
                    f"Axis {ax} is out of bounds for squeeze batch dims operation"
                )
            if input_batch_dims[ax] == 1:
                new_batch_dims[ax] = None
            else:
                raise ValueError(
                    f"Cannot squeeze batch axis {ax} of size {input_batch_dims[ax]} (must be 1)"
                )

        new_batch_dims = [dim for dim in new_batch_dims if dim is not None]
        return tuple(new_batch_dims)

    def forward(self, *args: Tensor) -> Tensor:
        """Override forward to handle case where no squeezing needed."""
        if len(args) != 1:
            raise ValueError(
                f"Squeeze batch dims operation requires 1 argument, got {len(args)}"
            )
        return super().forward(*args)

    def maxpr(self, args: list[TensorValue], output: Tensor) -> None:
        """MAX graph implementation using ops.squeeze."""
        axes = [ax - len(output.shape) for ax in self.axes]
        res = args[0]
        for ax in axes:
            res = ops.squeeze(res, ax)
        output.tensor_value = res

    def eagerxpr(self, args: list[Tensor], output: Tensor) -> None:
        """Eager execution using NumPy squeeze."""
        axes = [ax - len(args[0].shape) for ax in self.axes]
        np_result = np.squeeze(args[0].to_numpy(), axis=tuple(axes))
        output.impl_(np_result)

    def vjp_rule(
        self, _primals: list[Tensor], cotangent: Tensor, _output: Tensor
    ) -> list[Tensor]:
        """VJP rule: unsqueeze the cotangent back to original batch dimensions."""
        return [unsqueeze_batch_dims(cotangent, self.axes)]

    def jvp_rule(
        self, _primals: list[Tensor], tangents: list[Tensor], _output: Tensor
    ) -> Tensor:
        """JVP rule: apply squeeze to tangents."""
        return squeeze_batch_dims(tangents[0], self.axes)


def squeeze_batch_dims(arg: Tensor, axes: list[int] | None = None) -> Tensor:
    """Squeeze tensor by removing batch dimensions of size 1.

    Parameters
    ----------
        arg: Input tensor
        axes: List of batch dimension axes to squeeze. If None, returns tensor unchanged.

    Returns
    -------
        Tensor with specified batch dimensions of size 1 removed
    """
    if axes is None:
        return arg
    # Convert to negative indices for consistency with batch dimension handling
    axes = [ax if ax < 0 else -len(arg.batch_dims) + ax for ax in axes]
    op = SqueezeBatchDimsOp(axes)
    return op.forward(arg)


class UnsqueezeBatchDimsOp(ViewOperation):
    """Unsqueeze operation to add batch dimensions of size 1."""

    def __init__(self, axes: list[int] | None = None):
        super().__init__(f"unsqueeze_batch_dims[axes={axes}]")
        self.axes = sorted(axes) if axes is not None else []

    def compute_output_shape(self, *input_shapes: tuple) -> tuple:
        """Shape stays the same for batch dimension operations."""
        if len(input_shapes) != 1:
            raise ValueError(
                f"Unsqueeze batch dims operation requires 1 input shape, got {len(input_shapes)}"
            )
        return input_shapes[0]

    def compute_output_batch_dims(self, *input_batch_dimss: tuple) -> tuple:
        """Compute output batch_dims for unsqueeze operation."""
        if len(input_batch_dimss) != 1:
            raise ValueError(
                f"Unsqueeze batch dims operation requires 1 input batch_dims, got {len(input_batch_dimss)}"
            )
        input_batch_dims = input_batch_dimss[0]

        new_batch_dims = list(input_batch_dims)
        for ax in self.axes:
            if ax < -len(new_batch_dims) - 1:
                raise ValueError(
                    f"Axis {ax} is out of bounds for unsqueeze batch dims operation"
                )
            if ax + 1 <= -1:
                new_batch_dims.insert(ax + 1, 1)
            else:
                new_batch_dims.append(1)

        return tuple(new_batch_dims)

    def forward(self, *args: Tensor) -> Tensor:
        """Override forward to handle case where no unsqueezing needed."""
        if len(args) != 1:
            raise ValueError(
                f"Unsqueeze batch dims operation requires 1 argument, got {len(args)}"
            )
        return super().forward(*args)

    def maxpr(self, args: list[TensorValue], output: Tensor) -> None:
        """MAX graph implementation using ops.unsqueeze."""
        res = args[0]
        # Use self.axes directly since it's already normalized to a list in __init__
        # Adjust axes for batch dimensions
        axes = [ax - len(output.shape) for ax in self.axes] if self.axes else []
        for ax in axes:
            res = ops.unsqueeze(res, ax)
        output.tensor_value = res

    def eagerxpr(self, args: list[Tensor], output: Tensor) -> None:
        """Eager execution using NumPy expand_dims."""
        if self.axes:
            # Apply expand_dims for each axis sequentially
            np_result = args[0].to_numpy()
            axes = [ax - len(args[0].shape) for ax in self.axes]
            for ax in axes:
                np_result = np.expand_dims(np_result, axis=ax)
        else:
            np_result = args[0].to_numpy()
        output.impl_(np_result)

    def vjp_rule(
        self, primals: list[Tensor], cotangent: Tensor, output: Tensor
    ) -> list[Tensor]:
        """VJP rule: squeeze the cotangent back to original batch dimensions."""
        return [squeeze_batch_dims(cotangent, self.axes)]

    def jvp_rule(
        self, primals: list[Tensor], tangents: list[Tensor], output: Tensor
    ) -> Tensor:
        """JVP rule: apply unsqueeze to tangents."""
        return unsqueeze_batch_dims(tangents[0], self.axes)


def unsqueeze_batch_dims(arg: Tensor, axes: list[int] | None = None) -> Tensor:
    """Unsqueeze tensor by adding batch dimensions of size 1.

    Parameters
    ----------
        arg: Input tensor
        axes: List of positions where to insert batch dimensions of size 1.
              If None, returns tensor unchanged.

    Returns
    -------
        Tensor with batch dimensions of size 1 added at specified positions
    """
    if axes is None:
        return arg

    # Convert to negative indices for consistency with batch dimension handling
    axes = [ax if ax < 0 else -len(arg.batch_dims) - 1 + ax for ax in axes]

    op = UnsqueezeBatchDimsOp(axes)
    return op.forward(arg)


# let's creata stack function which first creates a lsit of tensors wiht a new axis (via unsqueeze) and then concatenates them along that axis
def stack(tensors: list[Tensor], axis: int = 0) -> Tensor:
    """Stack tensors along a new axis.

    Parameters
    ----------
        tensors: List of tensors to stack
        axis: Axis along which to stack the tensors (default: 0)

    Returns
    -------
        Stacked tensor
    """
    if not tensors:
        raise ValueError("Stack operation requires at least one tensor")

    # Unsqueeze each tensor to add a new dimension at the specified axis
    unsqueezed_tensors = [unsqueeze(tensor, [axis]) for tensor in tensors]

    # Use concatenate to stack them along the new axis
    return concatenate(unsqueezed_tensors, axis=axis)
