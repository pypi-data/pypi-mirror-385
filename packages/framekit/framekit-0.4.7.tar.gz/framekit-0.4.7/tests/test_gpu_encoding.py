#!/usr/bin/env python3
"""Test script to verify GPU encoding with NVENC and CPU fallback."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from framekit import MasterScene, Scene, TextElement


def test_gpu_encoding():
    """Test GPU encoding (will auto-fallback to CPU if NVENC not available)."""
    print("=" * 60)
    print("Testing GPU Encoding with NVENC (auto-fallback to CPU)")
    print("=" * 60)

    # Create a simple scene
    master = MasterScene(
        output_filename="output_gpu_test.mp4",
        width=1920,
        height=1080,
        fps=60,
        quality="medium",
        use_gpu_encoding=True  # Enable GPU encoding
    )

    scene = Scene()

    # Add a simple text element
    text = (
        TextElement("GPU Encoding Test", size=80, color=(255, 255, 255))
        .position(960, 540, anchor='center')
        .set_background((50, 50, 50), alpha=200, padding=20)
        .set_duration(3.0)
        .start_at(0.0)
    )

    scene.add(text)
    master.add(scene)

    # Render
    print("\nStarting render...")
    master.render()

    print("\n✓ Rendering completed successfully!")
    print(f"✓ Output file: output_gpu_test.mp4")


def test_cpu_encoding():
    """Test CPU encoding explicitly."""
    print("\n" + "=" * 60)
    print("Testing CPU Encoding (forced)")
    print("=" * 60)

    # Create a simple scene
    master = MasterScene(
        output_filename="output_cpu_test.mp4",
        width=1920,
        height=1080,
        fps=60,
        quality="medium",
        use_gpu_encoding=False  # Disable GPU encoding
    )

    scene = Scene()

    # Add a simple text element
    text = (
        TextElement("CPU Encoding Test", size=80)
        .position(960, 540, anchor='center')
        .set_color((255, 255, 255))
        .set_background((50, 50, 50), alpha=200, padding=20)
        .set_duration(3.0)
        .start_at(0.0)
    )

    scene.add(text)
    master.add(scene)

    # Render
    print("\nStarting render...")
    master.render()

    print("\n✓ Rendering completed successfully!")
    print(f"✓ Output file: output_cpu_test.mp4")


if __name__ == "__main__":
    # Test GPU encoding (with auto-fallback)
    test_gpu_encoding()

    # Test CPU encoding (forced)
    test_cpu_encoding()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
