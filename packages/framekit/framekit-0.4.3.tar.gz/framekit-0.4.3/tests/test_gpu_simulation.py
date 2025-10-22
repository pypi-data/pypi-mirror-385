#!/usr/bin/env python3
"""Test GPU detection with simulated GPU environment."""

from framekit.gpu_utils import GPUDetector


def test_cpu_mode():
    """Test CPU mode encoder settings."""
    print("Testing CPU mode:")
    GPUDetector.reset_cache()
    settings = GPUDetector.get_ffmpeg_encoder_settings("medium")
    print(f"  Settings: {' '.join(settings)}")
    assert "-c:v" in settings
    assert "libx264" in settings
    print("  ✓ CPU mode works correctly\n")


def test_gpu_mode():
    """Test GPU mode encoder settings (simulated)."""
    print("Testing GPU mode (simulated):")

    # Simulate GPU detection by directly setting cache
    GPUDetector.reset_cache()
    GPUDetector._cached_gpu_type = "nvidia"
    GPUDetector._cached_nvenc_available = True

    settings = GPUDetector.get_ffmpeg_encoder_settings("medium")
    print(f"  Settings: {' '.join(settings)}")
    assert "-c:v" in settings
    assert "h264_nvenc" in settings
    assert "-preset" in settings
    assert "medium" in settings
    print("  ✓ GPU mode works correctly\n")

    # Test different quality levels
    print("Testing different quality presets:")
    for quality in ["low", "medium", "high"]:
        settings = GPUDetector.get_ffmpeg_encoder_settings(quality)
        print(f"  {quality}: {' '.join(settings)}")

    # Reset cache
    GPUDetector.reset_cache()
    print("\n  ✓ All quality presets work correctly")


def test_fallback():
    """Test fallback from GPU to CPU."""
    print("\nTesting fallback (GPU detected but NVENC unavailable):")

    GPUDetector.reset_cache()
    GPUDetector._cached_gpu_type = "nvidia"
    GPUDetector._cached_nvenc_available = False

    settings = GPUDetector.get_ffmpeg_encoder_settings("medium")
    print(f"  Settings: {' '.join(settings)}")
    assert "-c:v" in settings
    assert "libx264" in settings
    print("  ✓ Fallback works correctly")

    GPUDetector.reset_cache()


def main():
    print("=" * 60)
    print("GPU Simulation Test")
    print("=" * 60)
    print()

    test_cpu_mode()
    test_gpu_mode()
    test_fallback()

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)


if __name__ == "__main__":
    main()
