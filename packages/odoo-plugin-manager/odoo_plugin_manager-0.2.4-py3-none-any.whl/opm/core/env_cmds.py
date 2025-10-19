from __future__ import annotations
import typer
from ...core.env import load_config
from ...core.state import set_default_env, get_default_env
from ...core.utils import info

app = typer.Typer(help="Manage OPM environments")

@app.command("list")
def list_envs():
    cfg = load_config()
    envs = (cfg.data.get("environments") or {}).keys()
    cur = get_default_env()
    for name in envs:
        mark = " (current)" if name == cur else ""
        info(f"- {name}{mark}")
    if not envs:
        info("No environments defined. Using 'runtime' by default.")

@app.command("use")
def use_env(name: str):
    cfg = load_config()
    envs = cfg.data.get("environments") or {}
    if name not in envs:
        raise typer.BadParameter(f"Environment '{name}' not defined in opm.yaml")
    set_default_env(name)
    info(f"Default environment set to '{name}'.")

@app.command("current")
def current_env():
    cur = get_default_env()
    if cur:
        info(f"Current default environment: {cur}")
    else:
        info("No default environment selected. Using 'runtime' by default.")