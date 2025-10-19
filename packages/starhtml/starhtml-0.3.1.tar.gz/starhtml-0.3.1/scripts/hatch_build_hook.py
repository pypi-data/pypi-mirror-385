#!/usr/bin/env python3
"""
Hatchling build hook to build JavaScript from TypeScript during wheel creation.

This hook ensures that JavaScript handlers are built from TypeScript sources
before the wheel is packaged, allowing us to keep generated JS files out of git
while still including them in the distributed package.
"""

import subprocess
from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class JavaScriptBuildError(Exception):
    """Raised when JavaScript build fails."""

    pass


def run_command(cmd: list[str], cwd: Path | None = None) -> None:
    """Run a command and raise JavaScriptBuildError if it fails."""
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ Successfully ran: {' '.join(cmd)}")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}")
        print(f"   Exit code: {e.returncode}")
        print(f"   Stderr: {e.stderr}")
        print(f"   Stdout: {e.stdout}")
        raise JavaScriptBuildError(f"Failed to run {' '.join(cmd)}") from e


class CustomBuildHook(BuildHookInterface):
    """Build hook that builds JavaScript from TypeScript during packaging."""

    PLUGIN_NAME = "custom"

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        """
        Initialize the build hook and build JavaScript from TypeScript.

        This method:
        1. Checks if bun is available (required for building)
        2. Installs JavaScript dependencies if needed
        3. Builds JavaScript handlers from TypeScript sources
        4. Ensures the built files are available for packaging
        """
        root_path = Path(self.root)

        print("🔨 Building JavaScript handlers from TypeScript...")

        # Check if we're in the right directory
        if not (root_path / "typescript").exists():
            print("⚠️  No typescript directory found, skipping JavaScript build")
            return

        if not (root_path / "package.json").exists():
            print("⚠️  No package.json found, skipping JavaScript build")
            return

        # Check if bun is available
        try:
            run_command(["bun", "--version"], cwd=root_path)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ bun is not available - JavaScript build will be skipped")
            print("   This is expected in some CI environments where JS is pre-built")
            return

        # Install dependencies if node_modules doesn't exist
        if not (root_path / "node_modules").exists():
            print("📦 Installing JavaScript dependencies...")
            run_command(["bun", "install", "--frozen-lockfile"], cwd=root_path)

        # Build JavaScript from TypeScript
        print("🏗️  Building JavaScript handlers...")
        run_command(["bun", "run", "build"], cwd=root_path)

        # Verify the build outputs exist
        handlers_dir = root_path / "src" / "starhtml" / "static" / "js" / "handlers"
        if not handlers_dir.exists():
            raise JavaScriptBuildError(f"Handlers directory not created: {handlers_dir}")

        # Dynamically discover all built .js files instead of hardcoding
        built_files = list(handlers_dir.glob("*.js"))
        if not built_files:
            raise JavaScriptBuildError("No JavaScript files found after build")

        # Check that at least the core files exist
        core_files = {"index.js", "persist.js", "scroll.js", "resize.js"}
        built_file_names = {f.name for f in built_files}
        missing_core = core_files - built_file_names
        if missing_core:
            raise JavaScriptBuildError(f"Missing core JavaScript files after build: {missing_core}")

        print(f"✅ JavaScript build complete! Generated {len(built_files)} handler files:")
        for file in sorted(built_files):
            print(f"   - {file.name}")

        # Add all generated files to build artifacts so hatchling includes them
        artifacts = build_data.setdefault("artifacts", [])
        for file_path in built_files:
            rel_path = f"src/starhtml/static/js/handlers/{file_path.name}"
            if rel_path not in artifacts:
                artifacts.append(rel_path)

        print(f"📦 Added {len(built_files)} JavaScript handlers to build artifacts")
