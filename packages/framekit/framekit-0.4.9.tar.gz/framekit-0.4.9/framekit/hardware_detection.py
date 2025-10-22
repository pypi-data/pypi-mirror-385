"""Hardware capability detection for video encoding/decoding acceleration.

This module provides utilities to detect available hardware acceleration features
including GPU capabilities, hardware video encoders (NVENC, VAAPI, VideoToolbox),
and hardware video decoders (NVDEC, VAAPI, VideoToolbox).
"""

import subprocess
import platform
import os
from typing import Optional, Dict, List, Tuple


class HardwareCapabilities:
    """Singleton class to detect and cache hardware capabilities."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not HardwareCapabilities._initialized:
            self.system = platform.system()
            self.has_ffmpeg = self._check_ffmpeg()
            self.has_opengl_pbo = self._check_opengl_pbo()

            # Hardware encoder/decoder detection
            if self.has_ffmpeg:
                self.hw_encoders = self._detect_hw_encoders()
                self.hw_decoders = self._detect_hw_decoders()
            else:
                self.hw_encoders = []
                self.hw_decoders = []

            HardwareCapabilities._initialized = True
            self._print_capabilities()

    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is available."""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _check_opengl_pbo(self) -> bool:
        """Check if OpenGL PBO (Pixel Buffer Object) is supported."""
        try:
            # Try to import PyOpenGL and check for PBO support
            from OpenGL.GL import glGenBuffers, GL_PIXEL_PACK_BUFFER
            # If we can import these, PBO is likely supported
            # Actual support will be checked at runtime when OpenGL context is available
            return True
        except (ImportError, Exception):
            return False

    def _detect_hw_encoders(self) -> List[str]:
        """Detect available hardware video encoders via FFmpeg."""
        encoders = []

        try:
            result = subprocess.run(
                ['ffmpeg', '-hide_banner', '-encoders'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return encoders

            output = result.stdout

            # Platform-specific encoder detection
            if self.system == 'Darwin':  # macOS
                if 'h264_videotoolbox' in output:
                    encoders.append('h264_videotoolbox')
                if 'hevc_videotoolbox' in output:
                    encoders.append('hevc_videotoolbox')

            elif self.system == 'Linux':
                # NVIDIA NVENC
                if 'h264_nvenc' in output:
                    encoders.append('h264_nvenc')
                if 'hevc_nvenc' in output:
                    encoders.append('hevc_nvenc')

                # Intel/AMD VAAPI
                if 'h264_vaapi' in output:
                    encoders.append('h264_vaapi')
                if 'hevc_vaapi' in output:
                    encoders.append('hevc_vaapi')

            elif self.system == 'Windows':
                # NVIDIA NVENC
                if 'h264_nvenc' in output:
                    encoders.append('h264_nvenc')
                if 'hevc_nvenc' in output:
                    encoders.append('hevc_nvenc')

                # AMD AMF
                if 'h264_amf' in output:
                    encoders.append('h264_amf')
                if 'hevc_amf' in output:
                    encoders.append('hevc_amf')

                # Intel QSV
                if 'h264_qsv' in output:
                    encoders.append('h264_qsv')
                if 'hevc_qsv' in output:
                    encoders.append('hevc_qsv')

        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return encoders

    def _detect_hw_decoders(self) -> List[str]:
        """Detect available hardware video decoders via FFmpeg."""
        decoders = []

        try:
            result = subprocess.run(
                ['ffmpeg', '-hide_banner', '-decoders'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return decoders

            output = result.stdout

            # Platform-specific decoder detection
            if self.system == 'Darwin':  # macOS
                if 'h264_videotoolbox' in output or 'h264' in output:
                    decoders.append('h264')
                if 'hevc_videotoolbox' in output or 'hevc' in output:
                    decoders.append('hevc')

            elif self.system == 'Linux':
                # NVIDIA CUVID/NVDEC
                if 'h264_cuvid' in output:
                    decoders.append('h264_cuvid')
                if 'hevc_cuvid' in output:
                    decoders.append('hevc_cuvid')

                # VAAPI
                if 'h264_vaapi' in output or 'h264' in output:
                    decoders.append('h264')
                if 'hevc_vaapi' in output or 'hevc' in output:
                    decoders.append('hevc')

            elif self.system == 'Windows':
                # NVIDIA CUVID
                if 'h264_cuvid' in output:
                    decoders.append('h264_cuvid')
                if 'hevc_cuvid' in output:
                    decoders.append('hevc_cuvid')

                # QSV
                if 'h264_qsv' in output:
                    decoders.append('h264_qsv')
                if 'hevc_qsv' in output:
                    decoders.append('hevc_qsv')

        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return decoders

    def get_best_encoder(self, codec: str = 'h264') -> Tuple[Optional[str], bool]:
        """Get the best available encoder for the specified codec.

        Args:
            codec: Target codec ('h264' or 'hevc')

        Returns:
            Tuple of (encoder_name, is_hardware)
            Returns (None, False) if no encoder is available
        """
        if not self.has_ffmpeg:
            return (None, False)

        # Check hardware encoders first
        hw_encoder_map = {
            'h264': ['h264_nvenc', 'h264_videotoolbox', 'h264_vaapi', 'h264_qsv', 'h264_amf'],
            'hevc': ['hevc_nvenc', 'hevc_videotoolbox', 'hevc_vaapi', 'hevc_qsv', 'hevc_amf']
        }

        for encoder in hw_encoder_map.get(codec, []):
            if encoder in self.hw_encoders:
                return (encoder, True)

        # Fallback to software encoder
        sw_encoder_map = {
            'h264': 'libx264',
            'hevc': 'libx265'
        }

        return (sw_encoder_map.get(codec), False)

    def get_hw_decode_option(self, video_path: str) -> Tuple[Optional[str], Optional[str]]:
        """Get hardware decode options for FFmpeg based on video file.

        Args:
            video_path: Path to video file

        Returns:
            Tuple of (hwaccel_method, hwaccel_device) or (None, None) if HW decode unavailable
        """
        if not self.has_ffmpeg or not self.hw_decoders:
            return (None, None)

        # Detect video codec
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet', '-select_streams', 'v:0',
                 '-show_entries', 'stream=codec_name', '-of', 'default=noprint_wrappers=1:nokey=1',
                 video_path],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return (None, None)

            codec = result.stdout.strip().lower()

        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return (None, None)

        # Platform-specific hardware acceleration
        if self.system == 'Darwin':  # macOS
            if codec in ['h264', 'hevc']:
                return ('videotoolbox', None)

        elif self.system == 'Linux':
            # Try CUDA (NVIDIA) first
            if f'{codec}_cuvid' in self.hw_decoders:
                return ('cuda', '0')
            # Fallback to VAAPI
            elif codec in ['h264', 'hevc']:
                return ('vaapi', '/dev/dri/renderD128')

        elif self.system == 'Windows':
            # Try CUDA (NVIDIA) first
            if f'{codec}_cuvid' in self.hw_decoders:
                return ('cuda', None)
            # Fallback to D3D11VA or DXVA2
            elif codec in ['h264', 'hevc']:
                return ('d3d11va', None)

        return (None, None)

    def _print_capabilities(self):
        """Print detected hardware capabilities."""
        print("=== Hardware Capabilities ===")
        print(f"Platform: {self.system}")
        print(f"FFmpeg: {'Available' if self.has_ffmpeg else 'Not found'}")
        print(f"OpenGL PBO: {'Supported' if self.has_opengl_pbo else 'Not supported'}")

        if self.has_ffmpeg:
            print(f"HW Encoders: {', '.join(self.hw_encoders) if self.hw_encoders else 'None'}")
            print(f"HW Decoders: {', '.join(self.hw_decoders) if self.hw_decoders else 'None'}")

            best_h264_enc, is_hw = self.get_best_encoder('h264')
            print(f"Best H.264 Encoder: {best_h264_enc} ({'HW' if is_hw else 'SW'})")

        print("============================\n")


# Global singleton instance
hw_caps = HardwareCapabilities()
