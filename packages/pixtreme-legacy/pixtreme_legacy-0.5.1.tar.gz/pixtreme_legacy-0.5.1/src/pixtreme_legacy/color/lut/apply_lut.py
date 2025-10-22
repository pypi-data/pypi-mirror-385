"""Legacy LUT functions for backward compatibility."""

import cupy as cp

from pixtreme.utils.dtypes import to_float32


def apply_lut_cp(image: cp.ndarray, lut: cp.ndarray, interpolation: int = 0) -> cp.ndarray:
    """
    Apply a 3D LUT to an image with trilinear interpolation.

    Parameters
    ----------
    image : cp.ndarray
        Input image. The shape is (height, width, 3). dtype is float32.
    lut : cp.ndarray
        Input LUT. The shape is (N, N, N, 3). dtype is float32.
    interpolation : int (optional)
        The interpolation method to use. by default 0, options are: 0 for trilinear, 1 for tetrahedral.

    Returns
    -------
    result : cp.ndarray
        Output image. The shape is (height, width, 3). dtype is float32.
    """
    try:
        image_rgb: cp.ndarray = to_float32(image)
        height, width, _ = image_rgb.shape
        result = cp.zeros_like(image_rgb)

        if interpolation == 0:
            # Get the number of LUT entries minus 1 (for zero-based indexing)
            N = lut.shape[0] - 1

            # Scale the image_rgb to the LUT size
            scaled_image_rgb = image_rgb * N

            # Calculate the indices for the corners of the cube for interpolation
            index_low = cp.floor(scaled_image_rgb).astype(cp.int32)
            index_high = cp.clip(index_low + 1, 0, N)

            # Calculate the fractional part for interpolation
            fractional = scaled_image_rgb - index_low

            # Interpolate
            for i in range(3):  # Iterate over each channel
                # Retrieve values from the LUT
                val000 = lut[index_low[..., 0], index_low[..., 1], index_low[..., 2], i]
                val001 = lut[index_low[..., 0], index_low[..., 1], index_high[..., 2], i]
                val010 = lut[index_low[..., 0], index_high[..., 1], index_low[..., 2], i]
                val011 = lut[index_low[..., 0], index_high[..., 1], index_high[..., 2], i]
                val100 = lut[index_high[..., 0], index_low[..., 1], index_low[..., 2], i]
                val101 = lut[index_high[..., 0], index_low[..., 1], index_high[..., 2], i]
                val110 = lut[index_high[..., 0], index_high[..., 1], index_low[..., 2], i]
                val111 = lut[index_high[..., 0], index_high[..., 1], index_high[..., 2], i]

                # Perform trilinear interpolation
                val00 = val000 * (1 - fractional[..., 0]) + val100 * fractional[..., 0]
                val01 = val001 * (1 - fractional[..., 0]) + val101 * fractional[..., 0]
                val10 = val010 * (1 - fractional[..., 0]) + val110 * fractional[..., 0]
                val11 = val011 * (1 - fractional[..., 0]) + val111 * fractional[..., 0]

                val0 = val00 * (1 - fractional[..., 1]) + val10 * fractional[..., 1]
                val1 = val01 * (1 - fractional[..., 1]) + val11 * fractional[..., 1]

                final_val = val0 * (1 - fractional[..., 2]) + val1 * fractional[..., 2]

                result[..., i] = final_val

                result = result.astype(cp.float32)

        elif interpolation == 1:
            # Get the number of LUT entries minus 1 (for zero-based indexing)
            dim = lut.shape[0]
            dim_minus_one = dim - 1

            # Scale the image_rgb to the LUT size
            scaled_image_rgb = cp.clip(image_rgb * dim_minus_one, 0, dim_minus_one - 1e-5)

            # Calculate the indices for the corners of the cube for interpolation
            index_floor = cp.floor(scaled_image_rgb).astype(cp.int32)
            index_ceil = cp.ceil(scaled_image_rgb).astype(cp.int32)

            # Calculate the fractional part for interpolation
            weights = scaled_image_rgb - index_floor

            # Interpolate
            for i in range(height):
                for j in range(width):
                    fx, fy, fz = weights[i, j]
                    if fx > fy:
                        if fy > fz:
                            w0, w1, w2, w3 = (1 - fx, fx - fy, fy - fz, fz)
                        elif fx > fz:
                            w0, w1, w2, w3 = (1 - fx, fx - fz, fz - fy, fy)
                        else:
                            w0, w1, w2, w3 = (1 - fz, fz - fx, fx - fy, fy)
                    else:
                        if fz > fy:
                            w0, w1, w2, w3 = (1 - fz, fz - fy, fy - fx, fx)
                        elif fz > fx:
                            w0, w1, w2, w3 = (1 - fy, fy - fz, fz - fx, fx)
                        else:
                            w0, w1, w2, w3 = (1 - fy, fy - fx, fx - fz, fz)

                    # Calculate corresponding LUT indices
                    indices = index_floor[i, j], index_ceil[i, j]
                    c000 = lut[indices[0][0], indices[0][1], indices[0][2]]
                    c100 = lut[indices[1][0], indices[0][1], indices[0][2]]
                    c110 = lut[indices[1][0], indices[1][1], indices[0][2]]
                    c111 = lut[indices[1][0], indices[1][1], indices[1][2]]

                    # Calculate interpolated color
                    result[i, j] = w0 * c000 + w1 * c100 + w2 * c110 + w3 * c111
        return result

    except Exception as e:
        print(f"Error apply_lut: {e}")
        raise e
