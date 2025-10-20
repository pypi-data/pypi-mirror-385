# src/opm/cli/commands/init.py
from pathlib import Path
import typer

DEFAULT_YAML = """\
platform: odoo

runtime:
  odoo_url: "http://localhost:10017"
  db: "main"
  user: "<user>"
  pass: "<password>"
  container: ""
  db_host: "<db>"
  db_port: 5432
  db_user: "<user>"
  db_password: "<password>"
  addons:
    - "<addons_path>"
  vite_proxy: "http://localhost:5173"
  ws_host: "127.0.0.1"
  ws_port: 8765
"""

def init():
  
  """
  Initialize a new OPM configuration file (opm.yaml).
  """
  
  target = Path("opm.yaml")
  if target.exists():
    typer.echo("[opm] opm.yaml already exists; skipped.")
    raise typer.Exit(0)
  target.write_text(DEFAULT_YAML, encoding="utf-8")
  typer.echo("[opm] ✅ Configuration created successfully at ./opm.yaml")