#!/usr/bin/env python3
"""Test GPU detection and configuration."""

from framekit import GPUDetector


def main():
    print("=" * 60)
    print("GPU Detection Test")
    print("=" * 60)

    # Test GPU type detection
    gpu_type = GPUDetector.detect_gpu_type()
    print(f"\nDetected GPU type: {gpu_type}")

    # Test NVENC availability
    nvenc_available = GPUDetector.is_nvenc_available()
    print(f"NVENC available: {nvenc_available}")

    # Test encoder settings for different quality levels
    print("\n" + "=" * 60)
    print("Encoder Settings by Quality Level")
    print("=" * 60)

    for quality in ["low", "medium", "high"]:
        settings = GPUDetector.get_ffmpeg_encoder_settings(quality)
        print(f"\n{quality.upper()} quality settings:")
        print(f"  Command args: {' '.join(settings)}")

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    if nvenc_available:
        print("\n✓ GPU acceleration is ENABLED")
        print("  - Video encoding will use NVIDIA NVENC (hardware acceleration)")
        print("  - OpenGL rendering will use GPU when available")
    else:
        if gpu_type == "nvidia":
            print("\n⚠ NVIDIA GPU detected but NVENC not available")
            print("  - FFmpeg may not have NVENC support compiled in")
            print("  - Video encoding will use CPU (libx264)")
        else:
            print("\n○ No GPU detected or GPU not supported")
            print("  - Video encoding will use CPU (libx264)")
            print("  - OpenGL rendering will use CPU or integrated GPU")

    print()


if __name__ == "__main__":
    main()
