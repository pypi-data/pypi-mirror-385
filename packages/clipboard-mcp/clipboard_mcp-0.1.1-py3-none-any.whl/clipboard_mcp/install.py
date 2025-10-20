#!/usr/bin/env python3
"""
Post-installation script for clipboard-mcp
Displays platform-specific dependency instructions
"""
import sys
import platform
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop


def post_install():
    """Display post-installation instructions based on the platform"""

    system = platform.system().lower()

    print("\n" + "=" * 70)
    print("  Clipboard MCP Server - Installation Complete!")
    print("=" * 70)

    if system == "linux":
        print("\n⚠️  LINUX USERS: Additional dependencies required")
        print("\nPlease install clipboard utilities:")
        print("  sudo apt install xclip xsel")
        print("\nOr for Wayland:")
        print("  sudo apt install wl-clipboard")
        print("\nAlternatively, install PyQt5 (larger dependency):")
        print("  pip install PyQt5")

    elif system == "darwin":
        print("\n✅ macOS: No additional dependencies needed")
        print("   (Uses built-in pbcopy/pbpaste)")

    elif system == "windows":
        print("\n✅ Windows: No additional dependencies needed")
        print("   (Uses built-in clip.exe and PowerShell)")

    print("\n" + "=" * 70)
    print("Documentation: https://github.com/gabiteodoru/clipboard-mcp")
    print("=" * 70 + "\n")


class PostInstallCommand(_install):
    """Post-installation for installation mode."""
    def run(self):
        _install.run(self)
        post_install()


class PostDevelopCommand(_develop):
    """Post-installation for development mode."""
    def run(self):
        _develop.run(self)
        post_install()


if __name__ == "__main__":
    post_install()
