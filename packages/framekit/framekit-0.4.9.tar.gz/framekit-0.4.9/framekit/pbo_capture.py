"""Pixel Buffer Object (PBO) based asynchronous frame capture for OpenGL.

This module provides efficient GPU-to-CPU frame transfer using double-buffered PBOs
to avoid blocking the rendering pipeline. Falls back to synchronous glReadPixels
if PBO is not supported.
"""

import numpy as np
from typing import Optional, Tuple
try:
    from OpenGL.GL import *
    from OpenGL.GL import GL_NO_ERROR
    HAS_OPENGL = True
except ImportError:
    HAS_OPENGL = False
    GL_NO_ERROR = 0


class PBOFrameCapture:
    """Asynchronous frame capture using Pixel Buffer Objects (PBO).

    This class implements double-buffered PBO to enable non-blocking frame capture
    from OpenGL. While one PBO is being read by the CPU, the GPU can write the next
    frame to the other PBO, effectively parallelizing CPU and GPU operations.

    Attributes:
        width: Frame width in pixels
        height: Frame height in pixels
        use_pbo: Whether PBO is available and enabled
        pbo_ids: List of PBO buffer IDs
        current_index: Current PBO buffer index (0 or 1)
        frame_ready: Whether a frame is ready to be retrieved
    """

    def __init__(self, width: int, height: int, use_pbo: bool = True):
        """Initialize PBO frame capture.

        Args:
            width: Frame width in pixels
            height: Frame height in pixels
            use_pbo: Whether to attempt using PBO (auto-falls back if unavailable)
        """
        self.width = width
        self.height = height
        self.use_pbo = use_pbo and HAS_OPENGL
        self.pbo_ids = []
        self.current_index = 0
        self.frame_ready = False

        # Calculate buffer size (RGBA, 4 bytes per pixel)
        self.buffer_size = width * height * 4

        if self.use_pbo:
            self._init_pbo()

    def _init_pbo(self):
        """Initialize PBO buffers."""
        if not HAS_OPENGL:
            self.use_pbo = False
            return

        try:
            # Check if PBO is supported
            if not glGenBuffers:
                print("Warning: PBO not supported, falling back to synchronous capture")
                self.use_pbo = False
                return

            # Create two PBOs for double buffering
            self.pbo_ids = glGenBuffers(2)

            # Initialize both PBOs with the required size
            for pbo_id in self.pbo_ids:
                glBindBuffer(GL_PIXEL_PACK_BUFFER, pbo_id)
                glBufferData(GL_PIXEL_PACK_BUFFER, self.buffer_size, None, GL_STREAM_READ)

            # Unbind PBO
            glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

            print(f"PBO initialized: {self.width}x{self.height}, double-buffered async capture enabled")

        except Exception as e:
            print(f"Warning: Failed to initialize PBO: {e}")
            print("Falling back to synchronous capture")
            self.use_pbo = False
            if self.pbo_ids:
                try:
                    glDeleteBuffers(len(self.pbo_ids), self.pbo_ids)
                except:
                    pass
                self.pbo_ids = []

    def start_capture(self):
        """Start asynchronous frame capture from current OpenGL framebuffer.

        This initiates a non-blocking read from the framebuffer into the current PBO.
        The actual data transfer happens asynchronously on the GPU.
        """
        if not self.use_pbo:
            # Synchronous path - nothing to start
            return

        try:
            # Save and reset OpenGL state to default for pixel operations
            glPushAttrib(GL_PIXEL_MODE_BIT)
            glPixelStorei(GL_PACK_ALIGNMENT, 1)

            # Bind the current PBO for writing
            glBindBuffer(GL_PIXEL_PACK_BUFFER, self.pbo_ids[self.current_index])

            # Start async read from framebuffer to PBO (non-blocking)
            glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE, None)

            # Unbind PBO
            glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

            # Restore OpenGL state
            glPopAttrib()

            self.frame_ready = True

        except Exception as e:
            print(f"Warning: PBO capture failed: {e}, falling back to sync")
            self.use_pbo = False

    def get_frame(self) -> Optional[np.ndarray]:
        """Retrieve the captured frame.

        For PBO: Retrieves data from the previously written PBO (double buffering)
        For non-PBO: Performs synchronous glReadPixels

        Returns:
            Frame data as numpy array (height, width, 4) in RGBA format, or None on error
        """
        if self.use_pbo:
            return self._get_frame_pbo()
        else:
            return self._get_frame_sync()

    def _get_frame_pbo(self) -> Optional[np.ndarray]:
        """Get frame using PBO (asynchronous method)."""
        if not self.frame_ready:
            return None

        try:
            # Save OpenGL state
            glPushAttrib(GL_PIXEL_MODE_BIT)
            glPixelStorei(GL_PACK_ALIGNMENT, 1)

            # Switch to the other PBO (the one we wrote to in the previous frame)
            read_index = self.current_index
            self.current_index = 1 - self.current_index  # Toggle between 0 and 1

            # Bind the PBO we want to read from
            glBindBuffer(GL_PIXEL_PACK_BUFFER, self.pbo_ids[read_index])

            # Map the PBO to CPU memory (this may block if GPU hasn't finished writing)
            buffer_ptr = glMapBuffer(GL_PIXEL_PACK_BUFFER, GL_READ_ONLY)

            if buffer_ptr is None:
                glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)
                glPopAttrib()
                return None

            # Copy data from mapped buffer to numpy array
            # Use frombuffer for zero-copy operation
            frame_data = np.frombuffer(
                buffer_ptr,
                dtype=np.uint8,
                count=self.buffer_size
            ).copy()  # Copy to ensure data persists after unmap

            # Unmap the buffer
            glUnmapBuffer(GL_PIXEL_PACK_BUFFER)

            # Unbind PBO
            glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)

            # Restore OpenGL state
            glPopAttrib()

            # Reshape to image dimensions
            frame = frame_data.reshape((self.height, self.width, 4))

            return frame

        except Exception as e:
            print(f"Warning: PBO frame retrieval failed: {e}")
            # Try to clean up
            try:
                glBindBuffer(GL_PIXEL_PACK_BUFFER, 0)
                glPopAttrib()
            except:
                pass
            # Fall back to sync for future frames
            self.use_pbo = False
            return self._get_frame_sync()

    def _get_frame_sync(self) -> Optional[np.ndarray]:
        """Get frame using synchronous glReadPixels (fallback method)."""
        try:
            # Clear any existing OpenGL errors
            while glGetError() != GL_NO_ERROR:
                pass

            # Set pixel storage mode
            glPixelStorei(GL_PACK_ALIGNMENT, 1)

            # Synchronous read (blocks until GPU finishes rendering)
            pixels = glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE)

            # Check for errors
            error = glGetError()
            if error != GL_NO_ERROR:
                print(f"OpenGL error during glReadPixels: {error}")
                return None

            frame = np.frombuffer(pixels, dtype=np.uint8)
            frame = frame.reshape((self.height, self.width, 4))

            return frame

        except Exception as e:
            print(f"Error: Synchronous frame capture failed: {e}")
            return None

    def resize(self, width: int, height: int):
        """Resize the capture buffers.

        Args:
            width: New frame width
            height: New frame height
        """
        if width == self.width and height == self.height:
            return

        self.width = width
        self.height = height
        self.buffer_size = width * height * 4

        if self.use_pbo:
            # Delete old PBOs
            self.cleanup()
            # Reinitialize with new size
            self._init_pbo()

    def cleanup(self):
        """Clean up PBO resources."""
        if self.use_pbo and len(self.pbo_ids) > 0:
            try:
                glDeleteBuffers(len(self.pbo_ids), self.pbo_ids)
            except:
                pass
            self.pbo_ids = []
            self.use_pbo = False

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()
