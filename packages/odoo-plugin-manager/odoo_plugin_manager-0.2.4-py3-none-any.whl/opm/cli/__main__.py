from __future__ import annotations
import typer
from rich import print
from .commands.dev import dev
from .commands.test import test
from .commands.init import init
from .commands.diagnose import diagnose

app = typer.Typer(add_completion=False, help="OPM - Plugin Manager for Odoo")

app.command()(init)
app.command()(diagnose)
app.command()(dev)
app.command()(test)

if __name__ == "__main__":
    app()