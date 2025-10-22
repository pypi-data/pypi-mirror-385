"""GPU detection and configuration utilities for FrameKit."""

import subprocess
import logging
from typing import Optional, Literal

logger = logging.getLogger(__name__)

GPUType = Literal["nvidia", "none"]


class GPUDetector:
    """Detects available GPU hardware and capabilities."""

    _cached_gpu_type: Optional[GPUType] = None
    _cached_nvenc_available: Optional[bool] = None

    @classmethod
    def detect_gpu_type(cls) -> GPUType:
        """
        Detect the type of GPU available in the system.

        Returns:
            "nvidia" if NVIDIA GPU is detected, "none" otherwise
        """
        if cls._cached_gpu_type is not None:
            return cls._cached_gpu_type

        # Try to detect NVIDIA GPU via nvidia-smi
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                gpu_name = result.stdout.strip()
                logger.info(f"Detected NVIDIA GPU: {gpu_name}")
                cls._cached_gpu_type = "nvidia"
                return "nvidia"
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.debug(f"nvidia-smi not available or failed: {e}")

        logger.info("No GPU detected, will use CPU")
        cls._cached_gpu_type = "none"
        return "none"

    @classmethod
    def is_nvenc_available(cls) -> bool:
        """
        Check if NVENC encoder is available in FFmpeg.

        Returns:
            True if h264_nvenc encoder is available
        """
        if cls._cached_nvenc_available is not None:
            return cls._cached_nvenc_available

        # First check if we have NVIDIA GPU
        if cls.detect_gpu_type() != "nvidia":
            cls._cached_nvenc_available = False
            return False

        # Check if FFmpeg has NVENC support
        try:
            result = subprocess.run(
                ["ffmpeg", "-hide_banner", "-encoders"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                has_nvenc = "h264_nvenc" in result.stdout
                cls._cached_nvenc_available = has_nvenc
                if has_nvenc:
                    logger.info("NVENC encoder available in FFmpeg")
                else:
                    logger.warning("NVIDIA GPU detected but FFmpeg does not have NVENC support")
                return has_nvenc
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.warning(f"Failed to check FFmpeg encoders: {e}")

        cls._cached_nvenc_available = False
        return False

    @classmethod
    def get_ffmpeg_encoder_settings(cls, quality: str = "medium") -> list[str]:
        """
        Get FFmpeg encoder settings based on available hardware.

        Args:
            quality: Encoding quality preset ("low", "medium", "high")

        Returns:
            List of FFmpeg command arguments for video encoding
        """
        if cls.is_nvenc_available():
            # NVENC settings
            # Map quality to NVENC presets
            nvenc_preset_map = {
                "low": "fast",
                "medium": "medium",
                "high": "slow"
            }
            preset = nvenc_preset_map.get(quality, "medium")

            return [
                "-c:v", "h264_nvenc",
                "-preset", preset,
                "-b:v", "5M",  # Target bitrate
                "-maxrate", "8M",  # Max bitrate
                "-bufsize", "10M",  # Buffer size
                "-profile:v", "high",
                "-rc", "vbr",  # Variable bitrate
            ]
        else:
            # CPU x264 settings
            x264_preset_map = {
                "low": "veryfast",
                "medium": "medium",
                "high": "slow"
            }
            preset = x264_preset_map.get(quality, "medium")

            return [
                "-c:v", "libx264",
                "-preset", preset,
                "-crf", "23",
                "-profile:v", "high",
            ]

    @classmethod
    def reset_cache(cls):
        """Reset cached detection results (useful for testing)."""
        cls._cached_gpu_type = None
        cls._cached_nvenc_available = None


def init_opengl_context(use_gpu: bool = True) -> bool:
    """
    Initialize OpenGL context with GPU support if available.

    Args:
        use_gpu: Whether to attempt GPU acceleration

    Returns:
        True if GPU context was initialized, False if falling back to CPU
    """
    if not use_gpu:
        logger.info("GPU disabled by configuration")
        return False

    gpu_type = GPUDetector.detect_gpu_type()

    if gpu_type == "nvidia":
        # Set environment variables for NVIDIA GPU
        import os
        # Use GPU 0 by default (can be overridden by user setting CUDA_VISIBLE_DEVICES)
        if "CUDA_VISIBLE_DEVICES" not in os.environ:
            os.environ["CUDA_VISIBLE_DEVICES"] = "0"

        # For headless environments with EGL
        os.environ["PYOPENGL_PLATFORM"] = "egl"

        logger.info("Initialized OpenGL with NVIDIA GPU support (EGL)")
        return True

    logger.info("Using default OpenGL context (CPU or integrated GPU)")
    return False
