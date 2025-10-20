"""Binary build script using PyInstaller."""

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def get_platform_name() -> str:
    """Get platform-specific binary name."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        return "nuha.exe"
    elif system == "darwin":
        if machine == "arm64":
            return "nuha-macos-arm64"
        return "nuha-macos-x64"
    else:  # Linux
        if machine in ["aarch64", "arm64"]:
            return "nuha-linux-arm64"
        return "nuha-linux-x64"


def build_binary(mode: str = "production") -> None:
    """Build standalone binary."""
    print(f"Building Nuha binary ({mode} mode)...")

    # Check if PyInstaller is installed
    try:
        import importlib.util

        if importlib.util.find_spec("PyInstaller") is None:
            raise ImportError
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"], check=True
        )

    # Build options
    options = [
        "nuha/cli/main.py",
        "--name=nuha",
        "--onefile",
        "--console",
        "--clean",
    ]

    if mode == "production":
        options.append("--strip")
        options.append("--optimize=2")

    # Add hidden imports
    hidden_imports = [
        "typer",
        "rich",
        "openai",
        "anthropic",
        "zhipuai",
        "pydantic",
        "cryptography",
        "toml",
    ]

    for imp in hidden_imports:
        options.append(f"--hidden-import={imp}")

    # Run PyInstaller
    subprocess.run([sys.executable, "-m", "PyInstaller"] + options, check=True)

    # Rename binary for platform
    dist_dir = Path("dist")
    original_name = "nuha" if platform.system() != "Windows" else "nuha.exe"
    platform_name = get_platform_name()

    if original_name != platform_name:
        original_path = dist_dir / original_name
        platform_path = dist_dir / platform_name
        if original_path.exists():
            shutil.move(str(original_path), str(platform_path))
            print(f"✓ Binary created: {platform_path}")
    else:
        print(f"✓ Binary created: {dist_dir / original_name}")


def create_installer(platform_type: str = "auto") -> None:
    """Create installer package."""
    print(f"Creating installer for {platform_type}...")

    if platform_type == "auto":
        platform_type = platform.system().lower()

    if platform_type == "darwin":
        _create_macos_installer()
    elif platform_type == "windows":
        _create_windows_installer()
    else:
        _create_linux_installer()


def _create_macos_installer() -> None:
    """Create macOS installer."""
    print("Creating .pkg installer for macOS...")
    # This would require pkgbuild - placeholder for now
    print("macOS installer creation not implemented yet")


def _create_windows_installer() -> None:
    """Create Windows installer."""
    print("Creating .msi installer for Windows...")
    # This would require WiX toolset - placeholder for now
    print("Windows installer creation not implemented yet")


def _create_linux_installer() -> None:
    """Create Linux installer."""
    print("Creating .deb/.rpm packages for Linux...")
    # This would require fpm or similar - placeholder for now
    print("Linux installer creation not implemented yet")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build Nuha binary distribution")
    parser.add_argument(
        "mode",
        choices=["dev", "production", "installer"],
        default="production",
        help="Build mode",
    )
    parser.add_argument(
        "--platform",
        choices=["auto", "darwin", "linux", "windows"],
        default="auto",
        help="Target platform for installer",
    )

    args = parser.parse_args()

    if args.mode == "installer":
        create_installer(args.platform)
    else:
        build_binary(args.mode)


if __name__ == "__main__":
    main()
