#!/usr/bin/env python3
"""
GPU情報とOpenGL設定を確認するテストスクリプト
Linux環境でNvidia GPUが正しく使われているか診断
"""
import os
import platform
import subprocess

def check_nvidia_gpu():
    """Nvidia GPUとドライバーの確認"""
    print("=" * 60)
    print("2. NVIDIA GPU確認")
    print("=" * 60)

    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            print("✓ NVIDIA GPU検出成功")
        else:
            print("✗ nvidia-smi実行失敗")
    except FileNotFoundError:
        print("✗ nvidia-smiが見つかりません - NVIDIAドライバーが未インストール")
    print()

def check_egl_support():
    """EGL (headless OpenGL) サポート確認"""
    print("=" * 60)
    print("2. EGL (Headless OpenGL) サポート確認")
    print("=" * 60)

    try:
        from OpenGL import EGL
        from OpenGL.EGL import eglGetDisplay, eglInitialize, EGL_DEFAULT_DISPLAY
        from OpenGL.GL import glGetString, GL_VENDOR, GL_RENDERER, GL_VERSION

        # EGLディスプレイを取得
        display = eglGetDisplay(EGL_DEFAULT_DISPLAY)
        if display == EGL.EGL_NO_DISPLAY:
            print("✗ EGLディスプレイを取得できません")
            return False

        # EGL初期化
        major, minor = EGL.EGLint(), EGL.EGLint()
        if not eglInitialize(display, major, minor):
            print("✗ EGL初期化に失敗しました")
            return False

        print(f"✓ EGL利用可能: バージョン {major.value}.{minor.value}")
        print("  → X11なしでGPUレンダリングが可能です")

        # 簡易的なコンテキスト作成テスト
        try:
            from framekit.headless_context import HeadlessContext

            with HeadlessContext(100, 100, use_egl=True) as (context_type, _):
                if context_type == "egl":
                    print("✓ EGLコンテキスト作成成功")
                    return True
        except Exception as e:
            print(f"⚠ EGLコンテキスト作成エラー: {e}")
            return False

    except ImportError as e:
        print(f"✗ EGLがインストールされていません: {e}")
        print("  インストール: pip install PyOpenGL-EGL")
        return False
    except Exception as e:
        print(f"✗ EGLエラー: {e}")
        return False

    print()
    return True


def check_opengl_info():
    """OpenGL情報を確認 (Pygame経由)"""
    print("=" * 60)
    print("3. OpenGL設定確認 (Pygame/X11)")
    print("=" * 60)

    # 環境変数を設定
    os.environ['SDL_VIDEODRIVER'] = os.environ.get('SDL_VIDEODRIVER', 'x11')
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

    try:
        import pygame
        from OpenGL.GL import glGetString, GL_VENDOR, GL_RENDERER, GL_VERSION

        # 小さなOpenGLウィンドウを作成
        pygame.init()
        screen = pygame.display.set_mode((100, 100), pygame.DOUBLEBUF | pygame.OPENGL | pygame.HIDDEN)

        # OpenGL情報を取得
        vendor = glGetString(GL_VENDOR)
        renderer = glGetString(GL_RENDERER)
        version = glGetString(GL_VERSION)

        print(f"Vendor:   {vendor.decode('utf-8') if vendor else 'N/A'}")
        print(f"Renderer: {renderer.decode('utf-8') if renderer else 'N/A'}")
        print(f"Version:  {version.decode('utf-8') if version else 'N/A'}")

        renderer_str = renderer.decode('utf-8').lower() if renderer else ""

        if 'nvidia' in renderer_str or 'geforce' in renderer_str or 'rtx' in renderer_str or 'quadro' in renderer_str:
            print("\n✓ NVIDIA GPUがOpenGLで使用されています")
        elif 'llvmpipe' in renderer_str or 'softpipe' in renderer_str:
            print("\n✗ 警告: ソフトウェアレンダリング(Mesa llvmpipe)が使われています!")
            print("  → NVIDIAドライバーが正しく設定されていない可能性があります")
        elif 'apple' in renderer_str or 'metal' in renderer_str:
            print("\n✓ Apple Metal/GPUが使用されています")
        else:
            print(f"\n⚠ 不明なレンダラー: {renderer_str}")

        pygame.quit()

    except Exception as e:
        print(f"✗ OpenGL初期化エラー: {e}")
        print("  → DISPLAYが設定されていないか、X11サーバーが起動していません")
        print("  解決策:")
        print("    1. Xvfbを使用: xvfb-run -a python tests/test_gpu_info.py")
        print("    2. EGLを使用 (上記でEGL利用可能な場合)")
    print()

def check_environment():
    """環境変数とシステム情報を確認"""
    print("=" * 60)
    print("1. システム環境")
    print("=" * 60)

    print(f"Platform: {platform.system()}")
    print(f"Python:   {platform.python_version()}")

    env_vars = [
        'SDL_VIDEODRIVER',
        'SDL_AUDIODRIVER',
        'DISPLAY',
        'LIBGL_ALWAYS_SOFTWARE',
        'MESA_GL_VERSION_OVERRIDE',
    ]

    print("\n環境変数:")
    for var in env_vars:
        value = os.environ.get(var, '(未設定)')
        print(f"  {var}: {value}")
    print()

def check_nvenc():
    """NVENC (GPU エンコーディング) の確認"""
    print("=" * 60)
    print("5. NVENC (GPU エンコーディング) 確認")
    print("=" * 60)

    try:
        result = subprocess.run(['ffmpeg', '-hide_banner', '-encoders'],
                               capture_output=True, text=True, timeout=5)

        if 'h264_nvenc' in result.stdout:
            print("✓ h264_nvenc が利用可能")
        else:
            print("✗ h264_nvenc が見つかりません")
            print("  → FFmpegがNVENCサポート付きでビルドされていない可能性")

        if 'hevc_nvenc' in result.stdout:
            print("✓ hevc_nvenc が利用可能")
    except Exception as e:
        print(f"✗ FFmpeg確認エラー: {e}")
    print()

def main():
    print("\n🔍 FrameKit GPU診断スクリプト\n")

    check_environment()
    check_nvidia_gpu()
    egl_available = check_egl_support()
    check_opengl_info()
    check_nvenc()

    print("=" * 60)
    print("診断完了")
    print("=" * 60)
    print("\n推奨アクション:")

    if not egl_available:
        print("\n【重要】EGLが利用できません:")
        print("  1. PyOpenGL-EGLをインストール:")
        print("     pip install PyOpenGL-EGL")
        print("  2. または、Xvfbを使用:")
        print("     sudo apt-get install xvfb")
        print("     xvfb-run -a -s '-screen 0 1920x1080x24' python your_script.py")

    print("\n【その他のトラブルシューティング】")
    print("1. Rendererに'llvmpipe'と表示された場合:")
    print("   → NVIDIAドライバーの再インストールが必要")
    print("2. NVENCが利用不可の場合:")
    print("   → NVENC対応FFmpegのインストールが必要")
    print("3. Dockerコンテナ内の場合:")
    print("   → nvidia-container-toolkitをインストール")
    print("   → --gpus all オプションでコンテナを起動")
    print("   → EGLを使用してX11なしでレンダリング")

if __name__ == "__main__":
    main()
