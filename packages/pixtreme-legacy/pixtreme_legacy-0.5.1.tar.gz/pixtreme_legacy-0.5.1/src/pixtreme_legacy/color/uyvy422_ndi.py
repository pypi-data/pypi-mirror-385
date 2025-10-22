"""Legacy NDI UYVY422 conversion functions for backward compatibility."""

import cupy as cp

from pixtreme.transform.resize import resize


def ndi_uyvy422_to_ycbcr444_cp(uyvy_data: cp.ndarray) -> cp.ndarray:
    """
    Convert NDI UYVY422 to YCbCr444.

    Parameters
    ----------
    uyvy_data : cp.ndarray
        The input UYVY422 data. The 3d array of the shape (height, width, 2).

    Returns
    -------
    yuv444p : cp.ndarray
        The output YCbCr444 data. The 3d array of the shape (height, width, 3).
    """
    # channel 1: Y
    # channel 0: U and V, [U0, Y0, U1, Y1, ...]
    y_component = uyvy_data[:, :, 1]
    uv_component = uyvy_data[:, :, 0]

    # Divide U and V components
    uv_component_flat = uv_component.flatten()
    u_component_flat = uv_component_flat[0::2]
    v_component_flat = uv_component_flat[1::2]

    u_component = u_component_flat.reshape((y_component.shape[0], y_component.shape[1] // 2))
    v_component = v_component_flat.reshape((y_component.shape[0], y_component.shape[1] // 2))

    u_component = resize(u_component, (y_component.shape[0], y_component.shape[1]), interpolation=2)
    v_component = resize(v_component, (y_component.shape[0], y_component.shape[1]), interpolation=2)

    # Resize and place U and V components
    # Repeat U and V to each pixel
    yuv444p = cp.dstack((y_component, u_component, v_component))

    return yuv444p
