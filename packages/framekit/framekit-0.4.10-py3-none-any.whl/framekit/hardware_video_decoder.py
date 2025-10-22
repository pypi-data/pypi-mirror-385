"""Hardware-accelerated video decoder using FFmpeg.

This module provides hardware-accelerated video decoding via FFmpeg's hwaccel
features (NVDEC, VAAPI, VideoToolbox, etc.) with automatic fallback to software
decoding when hardware acceleration is unavailable.
"""

import subprocess
import numpy as np
import os
from typing import Optional, Tuple
from .hardware_detection import hw_caps


class HardwareVideoDecoder:
    """Hardware-accelerated video decoder with software fallback.

    This class uses FFmpeg with hardware acceleration to decode video frames.
    It automatically detects the best available hardware decoder for the system
    and falls back to software decoding if hardware acceleration fails.

    Attributes:
        video_path: Path to the video file
        width: Video width in pixels
        height: Video height in pixels
        fps: Video frame rate
        total_frames: Total number of frames in the video
        use_hw_decode: Whether hardware decode is being used
        ffmpeg_process: FFmpeg subprocess for frame extraction
    """

    def __init__(self, video_path: str):
        """Initialize hardware video decoder.

        Args:
            video_path: Path to video file
        """
        self.video_path = video_path
        self.width = 0
        self.height = 0
        self.fps = 30.0
        self.total_frames = 0
        self.use_hw_decode = False
        self.ffmpeg_process = None
        self._current_frame_index = -1
        self._frame_cache = {}
        self._max_cache_size = 60  # Cache up to 60 frames (1 second at 60fps)

        # Get video properties and check HW decode availability
        self._probe_video()

    def _probe_video(self):
        """Probe video file to get properties."""
        if not os.path.exists(self.video_path):
            print(f"Warning: Video file not found: {self.video_path}")
            return

        try:
            # Get video properties using ffprobe
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet', '-print_format', 'json',
                 '-show_streams', '-select_streams', 'v:0', self.video_path],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                print(f"Warning: Failed to probe video: {self.video_path}")
                return

            import json
            data = json.loads(result.stdout)

            if not data.get('streams'):
                print(f"Warning: No video stream found: {self.video_path}")
                return

            stream = data['streams'][0]

            self.width = int(stream.get('width', 0))
            self.height = int(stream.get('height', 0))

            # Get FPS
            fps_str = stream.get('r_frame_rate', '30/1')
            if '/' in fps_str:
                num, den = map(int, fps_str.split('/'))
                self.fps = num / den if den != 0 else 30.0
            else:
                self.fps = float(fps_str)

            # Get total frames
            nb_frames = stream.get('nb_frames')
            if nb_frames:
                self.total_frames = int(nb_frames)
            else:
                # Estimate from duration
                duration = float(stream.get('duration', 0))
                if duration > 0:
                    self.total_frames = int(duration * self.fps)

        except Exception as e:
            print(f"Warning: Failed to probe video {self.video_path}: {e}")

    def get_frame_at_time(self, time: float) -> Optional[np.ndarray]:
        """Get frame at specific time using hardware decode.

        Args:
            time: Time in seconds

        Returns:
            Frame as numpy array (height, width, 3) in RGB format, or None on error
        """
        frame_index = int(time * self.fps)
        return self.get_frame_at_index(frame_index)

    def get_frame_at_index(self, frame_index: int) -> Optional[np.ndarray]:
        """Get frame at specific index using hardware decode.

        Args:
            frame_index: Frame index (0-based)

        Returns:
            Frame as numpy array (height, width, 3) in RGB format, or None on error
        """
        # Check cache first
        if frame_index in self._frame_cache:
            return self._frame_cache[frame_index]

        # Get frame using FFmpeg
        frame = self._decode_frame(frame_index)

        # Cache the frame
        if frame is not None:
            self._frame_cache[frame_index] = frame

            # Limit cache size
            if len(self._frame_cache) > self._max_cache_size:
                # Remove oldest frame (simple FIFO)
                oldest_key = min(self._frame_cache.keys())
                del self._frame_cache[oldest_key]

        return frame

    def _decode_frame(self, frame_index: int) -> Optional[np.ndarray]:
        """Decode a specific frame using FFmpeg.

        Args:
            frame_index: Frame index to decode

        Returns:
            Decoded frame or None on error
        """
        if self.width == 0 or self.height == 0:
            return None

        try:
            # Build FFmpeg command
            cmd = ['ffmpeg']

            # Add hardware decode options if available
            hwaccel, hwaccel_device = hw_caps.get_hw_decode_option(self.video_path)
            if hwaccel:
                cmd.extend(['-hwaccel', hwaccel])
                if hwaccel_device:
                    cmd.extend(['-hwaccel_device', hwaccel_device])
                self.use_hw_decode = True
            else:
                self.use_hw_decode = False

            # Input file
            cmd.extend(['-i', self.video_path])

            # Seek to specific frame
            cmd.extend(['-vf', f'select=eq(n\\,{frame_index})'])

            # Output format: single frame as rawvideo RGB24
            cmd.extend([
                '-vframes', '1',
                '-f', 'rawvideo',
                '-pix_fmt', 'rgb24',
                '-'
            ])

            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=5
            )

            if result.returncode != 0:
                # Hardware decode might have failed, try software decode
                if self.use_hw_decode:
                    return self._decode_frame_software(frame_index)
                return None

            # Convert raw bytes to numpy array
            frame_size = self.width * self.height * 3
            if len(result.stdout) < frame_size:
                return None

            frame = np.frombuffer(result.stdout, dtype=np.uint8, count=frame_size)
            frame = frame.reshape((self.height, self.width, 3))

            return frame

        except subprocess.TimeoutExpired:
            print(f"Warning: Frame decode timeout at index {frame_index}")
            return None
        except Exception as e:
            print(f"Warning: Frame decode failed at index {frame_index}: {e}")
            return None

    def _decode_frame_software(self, frame_index: int) -> Optional[np.ndarray]:
        """Fallback to software decoding.

        Args:
            frame_index: Frame index to decode

        Returns:
            Decoded frame or None on error
        """
        try:
            cmd = [
                'ffmpeg',
                '-i', self.video_path,
                '-vf', f'select=eq(n\\,{frame_index})',
                '-vframes', '1',
                '-f', 'rawvideo',
                '-pix_fmt', 'rgb24',
                '-'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=5
            )

            if result.returncode != 0:
                return None

            frame_size = self.width * self.height * 3
            if len(result.stdout) < frame_size:
                return None

            frame = np.frombuffer(result.stdout, dtype=np.uint8, count=frame_size)
            frame = frame.reshape((self.height, self.width, 3))

            return frame

        except Exception as e:
            print(f"Warning: Software decode failed at index {frame_index}: {e}")
            return None

    def clear_cache(self):
        """Clear the frame cache."""
        self._frame_cache.clear()

    def __del__(self):
        """Cleanup resources."""
        self.clear_cache()
        if self.ffmpeg_process:
            try:
                self.ffmpeg_process.terminate()
                self.ffmpeg_process.wait(timeout=1)
            except:
                try:
                    self.ffmpeg_process.kill()
                except:
                    pass
