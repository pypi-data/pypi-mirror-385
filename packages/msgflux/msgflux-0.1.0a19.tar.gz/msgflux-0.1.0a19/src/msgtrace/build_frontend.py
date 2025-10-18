#!/usr/bin/env python3
"""Build script for msgtrace frontend."""

import subprocess
import sys
from pathlib import Path


def build_frontend():
    """Build the frontend using npm."""
    frontend_dir = Path(__file__).parent / "frontend"

    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False

    print("📦 Installing frontend dependencies...")
    result = subprocess.run(
        ["npm", "install"],
        cwd=frontend_dir,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("❌ Failed to install dependencies:")
        print(result.stderr)
        return False

    print("✅ Dependencies installed")

    print("🔨 Building frontend...")
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=frontend_dir,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("❌ Failed to build frontend:")
        print(result.stderr)
        return False

    print("✅ Frontend built successfully")

    # Check if dist exists
    dist_dir = frontend_dir / "dist"
    if dist_dir.exists():
        print(f"📁 Build output: {dist_dir}")
        print(f"📊 Build size: {sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file()) / 1024:.2f} KB")
        return True
    else:
        print("❌ Build directory not found")
        return False


if __name__ == "__main__":
    success = build_frontend()
    sys.exit(0 if success else 1)
