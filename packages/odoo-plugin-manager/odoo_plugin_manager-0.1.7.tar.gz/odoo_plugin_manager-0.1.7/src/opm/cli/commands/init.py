# src/opm/cli/commands/init.py
from __future__ import annotations
import typer, shutil
from pathlib import Path
from ...core.utils import info

def init():
    """
    Initialize a new OPM project in the current directory.
    """
    root = Path(".")
    example = root / "opm.example.yaml"
    target = root / "opm.yaml"

    if not target.exists():
        if example.exists():
            shutil.copy(example, target)
            info("✅ Created opm.yaml configuration file.")
        else:
            info("⚠️  Missing opm.example.yaml — please create opm.yaml manually.")
    else:
        info("ℹ️  opm.yaml already exists, skipping creation.")

    Path(".opm").mkdir(exist_ok=True)
    Path("dist").mkdir(exist_ok=True)
    info("✅ Created .opm/ and dist/ directories.")
    info("🎉 Project initialized successfully.")
    info("Next steps:")
    info("  • Run `opm dev` to start watching for changes.")
    info("  • Run `opm test <module>` to execute tests inside Docker.")