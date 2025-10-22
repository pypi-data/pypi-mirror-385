"""Legacy YUV420 conversion functions for backward compatibility."""

import cupy as cp

from pixtreme.transform.resize import resize


def yuv420p_to_ycbcr444_cp(yuv420_data: cp.ndarray, width: int, height: int, interpolation: int = 1) -> cp.ndarray:
    """
    Convert YUV 4:2:0 to YCbCr 4:4:4

    Parameters
    ----------
    yuv420_data : cp.ndarray
        Input frame. Shape 1D array (uint8).
    width : int
        Width of the frame.
    height : int
        Height of the frame.
    interpolation : int
        Interpolation method (0=nearest, 1=bilinear, 2=bicubic).

    Returns
    -------
    image_ycbcr444 : cp.ndarray
        Output frame. Shape 3D array (height, width, 3) in YCbCr 4:4:4 format.
    """
    # Calculate the size of the Y and UV data
    y_data_size = width * height
    uv_data_size = width * height // 4

    # Normalize the input frame
    yuv420_data = yuv420_data.astype(cp.float32) / 255.0

    # Split the Y, U, and V data
    y_data = yuv420_data[:y_data_size]
    u_data = yuv420_data[y_data_size : y_data_size + uv_data_size]
    v_data = yuv420_data[y_data_size + uv_data_size : y_data_size + uv_data_size * 2]

    # Reshape the Y, U, and V data to 2D arrays
    y_image = y_data.reshape((height, width))
    u_image = u_data.reshape((height // 2, width // 2))
    v_image = v_data.reshape((height // 2, width // 2))

    # Scale the U and V data with bilinear interpolation
    u_scaled = None
    v_scaled = None
    if interpolation == 0:
        u_scaled = resize(u_image, (width, height), interpolation=0)
        v_scaled = resize(v_image, (width, height), interpolation=0)
    elif interpolation == 1:
        u_scaled = resize(u_image, (width, height), interpolation=1)
        v_scaled = resize(v_image, (width, height), interpolation=1)
    elif interpolation == 2:
        u_scaled = resize(u_image, (width, height), interpolation=2)
        v_scaled = resize(v_image, (width, height), interpolation=2)

    # Stack the Y, U, and V data to form the output frame
    image_ycbcr444 = cp.dstack([y_image, u_scaled, v_scaled])

    return image_ycbcr444
