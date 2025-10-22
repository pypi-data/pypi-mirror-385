"""Tests for pixtreme-legacy package."""

import warnings

import pytest


def test_import_legacy_package():
    """Test that pixtreme_legacy package can be imported."""
    import pixtreme_legacy

    assert pixtreme_legacy.__version__ == "0.5.0"


def test_all_exports():
    """Test that all expected functions are exported."""
    import pixtreme_legacy

    expected_exports = [
        "apply_lut_cp",
        "uyvy422_to_ycbcr444_cp",
        "ndi_uyvy422_to_ycbcr444_cp",
        "yuv420p_to_ycbcr444_cp",
        "yuv422p10le_to_ycbcr444_cp",
    ]

    for name in expected_exports:
        assert hasattr(pixtreme_legacy, name), f"Missing export: {name}"


def test_functions_are_callable():
    """Test that all exported functions are callable."""
    import pixtreme_legacy

    for name in pixtreme_legacy.__all__:
        if name != "__version__":
            func = getattr(pixtreme_legacy, name)
            assert callable(func), f"{name} is not callable"


def test_deprecation_warnings_are_present():
    """Test that calling _cp functions triggers DeprecationWarning."""
    import cupy as cp

    from pixtreme_legacy import apply_lut_cp

    # Create dummy data
    image = cp.random.rand(10, 10, 3).astype(cp.float32)
    lut = cp.random.rand(17, 17, 17, 3).astype(cp.float32)

    # Should trigger DeprecationWarning
    with pytest.warns(DeprecationWarning, match="apply_lut_cp is deprecated"):
        result = apply_lut_cp(image, lut)

    assert result.shape == image.shape


def test_import_from_pixtreme_still_works():
    """Test that _cp functions can still be imported from main pixtreme package."""
    from pixtreme.color import uyvy422_to_ycbcr444_cp
    from pixtreme.color.lut import apply_lut_cp

    assert callable(apply_lut_cp)
    assert callable(uyvy422_to_ycbcr444_cp)


def test_readme_exists():
    """Test that README.md exists in the legacy package."""
    import pathlib

    legacy_dir = pathlib.Path(__file__).parent.parent
    readme_path = legacy_dir / "README.md"
    assert readme_path.exists(), "README.md not found"
    assert readme_path.stat().st_size > 0, "README.md is empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
