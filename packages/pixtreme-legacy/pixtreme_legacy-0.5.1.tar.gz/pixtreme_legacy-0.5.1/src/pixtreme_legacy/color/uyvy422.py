"""Legacy UYVY422 conversion functions for backward compatibility."""

import cupy as cp


def uyvy422_to_ycbcr444_cp(uyvy_data: cp.ndarray, height: int, width: int) -> cp.ndarray:
    """
    Convert UYVY422 to YCbCr444.

    Parameters
    ----------
    uyvy_data : cp.ndarray
        The input UYVY422 data. The 1d array of the shape (height * width * 2).
    height : int
        The height of the input image.
    width : int
        The width of the input image.

    Returns
    -------
    yuv444p : cp.ndarray
        The output YCbCr444 data. The 3d array of the shape (height, width, 3).
    """
    # Convert UYVY data to 2D and make each row U0, Y0, V0, Y1, ...
    uyvy_2d = uyvy_data.reshape(height, width * 2)

    # Initialize the output array in YUV444P format
    yuv444p = cp.zeros((height, width, 3), dtype=cp.uint8)

    # Extract Y0 and Y1 and place them in the Y channel
    yuv444p[:, :, 0] = uyvy_2d[:, 1::2]  # Extract Y0 and Y1 and place them in Y channel

    # Construct U and V components
    u = uyvy_2d[:, 0::4]  # Pick U every 4 bytes
    v = uyvy_2d[:, 2::4]  # Pick V every 4 bytes

    # Resize and place U and V components
    # Repeat U and V to each pixel
    yuv444p[:, :, 1] = cp.repeat(u, 2, axis=1)
    yuv444p[:, :, 2] = cp.repeat(v, 2, axis=1)

    return yuv444p
