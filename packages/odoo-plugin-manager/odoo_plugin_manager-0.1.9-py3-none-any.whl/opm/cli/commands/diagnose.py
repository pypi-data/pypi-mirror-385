from __future__ import annotations
import subprocess
import typer
import requests

from ...core.utils import which, info
from ...core.env import load_config
from ...core.odoo_rpc import OdooRPC


def _check(cmd: str) -> str:
    path = which(cmd)
    return f"✅ Found ({path})" if path else "❌ Not found"


def diagnose(
    env: str | None = typer.Option(None, "--env", "-e", help="Environment name (from opm.yaml 'environments'); if not provided, uses runtime"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show extra details"),
    check_auth: bool = typer.Option(False, "--check-auth", help="Attempt XML-RPC authentication using configured DB/user/pass"),
):
    """Check Docker, Odoo reachability, and optional XML-RPC authentication."""
    cfg = load_config()

    info("🔍 Running environment diagnostics...")
    info(f"Docker CLI: {_check('docker')}")

    # Check local Odoo binary only if relevant (local profile) or when verbose
    profile = getattr(cfg, 'profile', cfg.data.get('profile', 'docker'))
    if verbose or profile == 'local':
        od = which('odoo')
        if od:
            info(f"Odoo binary: ✅ Found ({od})")
        else:
            od2 = which('odoo-bin')
            info(f"Odoo binary: {'✅ Found ('+od2+')' if od2 else '❌ Not found'}")

    # Resolve environment or fallback to runtime
    used_env = env or 'runtime'
    data = None
    if env and hasattr(cfg, 'resolve_env'):
        try:
            resolved = cfg.resolve_env(env)
            data = resolved.data
        except Exception as e:
            raise typer.BadParameter(f"Environment '{env}' not found/invalid in opm.yaml: {e}")
    if data is None:
        data = {
            "odoo_url": cfg.get("runtime", "odoo_url"),
            "db": cfg.get("runtime", "db"),
            "user": cfg.get("runtime", "user"),
            "pass": cfg.get("runtime", "pass"),
        }

    url = data.get("odoo_url")
    info(f"Using environment '{used_env}' → URL: {url} | DB: {data.get('db')}")

    info(f"Testing Odoo URL: {url}")
    try:
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            info("✅ Odoo instance reachable.")
        else:
            info(f"⚠️  Odoo responded with status code: {r.status_code}")
    except Exception as e:
        info(f"❌ Could not reach Odoo: {e}")
        return

    if check_auth:
        info("🔐 Checking XML-RPC authentication...")
        rpc = OdooRPC(url, data.get("db"), data.get("user"), data.get("pass"))
        try:
            rpc.login()
            info("✅ Authentication successful.")
        except Exception as e:
            info("❌ Authentication failed. Verify DB name, username/email, password, and dbfilter.")
            info(f"   Details: {e}")

    if verbose and which("docker"):
        try:
            cp = subprocess.run(["docker", "version", "--format", "{{.Server.Version}}"], capture_output=True, text=True, timeout=3)
            if cp.returncode == 0:
                info(f"ℹ️  Docker server version: {cp.stdout.strip()}")
        except Exception:
            pass

    info("🏁 Diagnose complete.")