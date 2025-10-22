"""Legacy YUV422p10le conversion functions for backward compatibility."""

import cupy as cp


def yuv422p10le_to_ycbcr444_cp(ycbcr422_data: cp.ndarray, width: int, height: int) -> cp.ndarray:
    """
    Convert YCbCr 4:2:2 to YCbCr 4:4:4

    Parameters
    ----------
    ycbcr422_data : cp.ndarray
        Input frame. Shape 1D array (uint8).
    width : int
        Width of the frame.
    height : int
        Height of the frame.

    Returns
    -------
    frame_ycbcr444 : cp.ndarray
        Output frame. Shape 3D array (height, width, 3) in YCbCr 4:4:4 format.
    """
    y_data_size = width * height * 2
    uv_data_size = width * height

    yuv_data = ycbcr422_data.tobytes()

    y_data_bytes = yuv_data[:y_data_size]
    u_data_bytes = yuv_data[y_data_size : y_data_size + uv_data_size]
    v_data_bytes = yuv_data[y_data_size + uv_data_size : y_data_size + uv_data_size * 2]

    # Convert uint8 array directly to uint16 array with little-endian specification
    y_data = cp.frombuffer(y_data_bytes, dtype="<u2")
    u_data = cp.frombuffer(u_data_bytes, dtype="<u2")
    v_data = cp.frombuffer(v_data_bytes, dtype="<u2")

    # Get only lower 10 bits (ignore upper 6 bits)
    y_data = y_data & 0x03FF
    u_data = u_data & 0x03FF
    v_data = v_data & 0x03FF

    # Normalize
    y_data_normalized = y_data.astype(cp.float32) / 1023.0
    u_data_normalized = u_data.astype(cp.float32) / 1023.0
    v_data_normalized = v_data.astype(cp.float32) / 1023.0

    # Reshape to 2D arrays
    y_image = y_data_normalized.reshape((height, width))
    u_image = u_data_normalized.reshape((height, width // 2))
    v_image = v_data_normalized.reshape((height, width // 2))

    # Scale U and V horizontally by 2x
    u_scaled = cp.repeat(u_image, 2, axis=1)
    v_scaled = cp.repeat(v_image, 2, axis=1)

    # Combine Y, U, V to form (height, width, 3) shape
    frame_ycbcr444 = cp.stack([y_image, u_scaled, v_scaled], axis=2)

    return frame_ycbcr444
