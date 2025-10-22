"""
Headless OpenGL context creation for server/container environments.

Supports multiple backends:
1. EGL (NVIDIA GPU direct access, no X11 required)
2. Pygame with Xvfb (fallback)
"""
import os
import platform
from typing import Tuple, Optional


class HeadlessContext:
    """Manages headless OpenGL context creation across different platforms."""

    def __init__(self, width: int, height: int, use_egl: bool = True):
        """Initialize headless context manager.

        Args:
            width: Render width
            height: Render height
            use_egl: Try EGL first (Linux only), fallback to Pygame if False or unavailable
        """
        self.width = width
        self.height = height
        self.use_egl = use_egl and platform.system() == 'Linux'
        self.context_type = None
        self.display = None
        self.surface = None
        self.context = None
        self.pygame_screen = None

    def create(self) -> Tuple[str, any]:
        """Create headless OpenGL context.

        Returns:
            Tuple of (context_type, context_object)
            context_type: "egl", "pygame", or "pygame_xvfb"
            context_object: The created context (implementation-specific)
        """
        # Try EGL first on Linux
        if self.use_egl:
            try:
                context = self._create_egl_context()
                if context:
                    self.context_type = "egl"
                    return ("egl", context)
            except Exception as e:
                print(f"EGL initialization failed: {e}")
                print("Falling back to Pygame...")

        # Fallback to Pygame
        context = self._create_pygame_context()
        self.context_type = "pygame"
        return ("pygame", context)

    def _create_egl_context(self) -> Optional[dict]:
        """Create EGL context for headless rendering.

        Returns:
            Dictionary containing EGL display, surface, and context
        """
        try:
            from OpenGL import EGL
            from OpenGL.EGL import (
                EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
                EGL_BLUE_SIZE, EGL_GREEN_SIZE, EGL_RED_SIZE, EGL_ALPHA_SIZE,
                EGL_DEPTH_SIZE, EGL_RENDERABLE_TYPE, EGL_OPENGL_BIT,
                EGL_CONFORMANT, EGL_NONE, EGL_DEFAULT_DISPLAY,
                EGL_NO_CONTEXT, EGL_OPENGL_API,
                EGL_WIDTH, EGL_HEIGHT,
                eglGetDisplay, eglInitialize, eglChooseConfig,
                eglBindAPI, eglCreateContext, eglCreatePbufferSurface,
                eglMakeCurrent, eglGetError
            )
            from OpenGL.GL import glGetString, GL_VENDOR, GL_RENDERER, GL_VERSION

        except ImportError as e:
            print(f"EGL import failed: {e}")
            print("Install with: pip install PyOpenGL-EGL")
            return None

        # Get EGL display
        self.display = eglGetDisplay(EGL_DEFAULT_DISPLAY)
        if self.display == EGL.EGL_NO_DISPLAY:
            raise RuntimeError("Failed to get EGL display")

        # Initialize EGL
        major, minor = EGL.EGLint(), EGL.EGLint()
        if not eglInitialize(self.display, major, minor):
            raise RuntimeError(f"Failed to initialize EGL: {eglGetError()}")

        print(f"EGL Version: {major.value}.{minor.value}")

        # Configure EGL
        config_attribs = [
            EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
            EGL_BLUE_SIZE, 8,
            EGL_GREEN_SIZE, 8,
            EGL_RED_SIZE, 8,
            EGL_ALPHA_SIZE, 8,
            EGL_DEPTH_SIZE, 24,
            EGL_RENDERABLE_TYPE, EGL_OPENGL_BIT,
            EGL_CONFORMANT, EGL_OPENGL_BIT,
            EGL_NONE
        ]

        configs = (EGL.EGLConfig * 1)()
        num_configs = EGL.EGLint()

        if not eglChooseConfig(self.display, config_attribs, configs, 1, num_configs):
            raise RuntimeError(f"Failed to choose EGL config: {eglGetError()}")

        if num_configs.value == 0:
            raise RuntimeError("No suitable EGL configs found")

        # Bind OpenGL API
        if not eglBindAPI(EGL_OPENGL_API):
            raise RuntimeError(f"Failed to bind OpenGL API: {eglGetError()}")

        # Create EGL context
        self.context = eglCreateContext(self.display, configs[0], EGL_NO_CONTEXT, None)
        if self.context == EGL.EGL_NO_CONTEXT:
            raise RuntimeError(f"Failed to create EGL context: {eglGetError()}")

        # Create pbuffer surface
        pbuffer_attribs = [
            EGL_WIDTH, self.width,
            EGL_HEIGHT, self.height,
            EGL_NONE
        ]

        self.surface = eglCreatePbufferSurface(self.display, configs[0], pbuffer_attribs)
        if self.surface == EGL.EGL_NO_SURFACE:
            raise RuntimeError(f"Failed to create EGL surface: {eglGetError()}")

        # Make context current
        if not eglMakeCurrent(self.display, self.surface, self.surface, self.context):
            raise RuntimeError(f"Failed to make EGL context current: {eglGetError()}")

        # Verify OpenGL is working
        try:
            vendor = glGetString(GL_VENDOR)
            renderer = glGetString(GL_RENDERER)
            version = glGetString(GL_VERSION)

            vendor_str = vendor.decode('utf-8') if vendor else 'Unknown'
            renderer_str = renderer.decode('utf-8') if renderer else 'Unknown'
            version_str = version.decode('utf-8') if version else 'Unknown'

            print(f"✓ EGL Context Created Successfully")
            print(f"  Vendor:   {vendor_str}")
            print(f"  Renderer: {renderer_str}")
            print(f"  Version:  {version_str}")

            # Warn if software rendering
            if 'llvmpipe' in renderer_str.lower() or 'softpipe' in renderer_str.lower():
                print("⚠️  WARNING: Software rendering detected via EGL")
                print("   → GPU acceleration may not be working properly")

        except Exception as e:
            print(f"Warning: Could not query OpenGL info: {e}")

        return {
            'display': self.display,
            'surface': self.surface,
            'context': self.context
        }

    def _create_pygame_context(self) -> any:
        """Create Pygame OpenGL context (requires X11 or Xvfb).

        Returns:
            Pygame screen object
        """
        import pygame

        # Set environment for headless operation
        if 'SDL_VIDEODRIVER' not in os.environ:
            # Let Pygame auto-detect (will fail if no display)
            pass

        os.environ['SDL_AUDIODRIVER'] = 'dummy'
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
        os.environ['SDL_VIDEO_WINDOW_POS'] = '-1000,-1000'

        pygame.init()

        try:
            self.pygame_screen = pygame.display.set_mode(
                (self.width, self.height),
                pygame.DOUBLEBUF | pygame.OPENGL | pygame.HIDDEN
            )
            print("✓ Pygame OpenGL context created")
            return self.pygame_screen

        except pygame.error as e:
            raise RuntimeError(
                f"Failed to create Pygame OpenGL context: {e}\n"
                "For headless rendering, use one of:\n"
                "  1. Install and run with Xvfb: xvfb-run -a python your_script.py\n"
                "  2. Install EGL support: pip install PyOpenGL-EGL\n"
                "  3. Set DISPLAY environment variable to a valid X11 display"
            )

    def destroy(self):
        """Clean up OpenGL context."""
        if self.context_type == "egl":
            try:
                from OpenGL.EGL import (
                    eglMakeCurrent, eglDestroySurface, eglDestroyContext,
                    eglTerminate, EGL_NO_DISPLAY, EGL_NO_SURFACE, EGL_NO_CONTEXT
                )

                if self.display:
                    eglMakeCurrent(self.display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT)

                    if self.surface:
                        eglDestroySurface(self.display, self.surface)

                    if self.context:
                        eglDestroyContext(self.display, self.context)

                    eglTerminate(self.display)

            except Exception as e:
                print(f"Warning: EGL cleanup error: {e}")

        elif self.context_type == "pygame":
            try:
                import pygame
                pygame.quit()
            except:
                pass

    def __enter__(self):
        """Context manager entry."""
        return self.create()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.destroy()
