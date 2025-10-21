from __future__ import annotations
import shlex
from pathlib import Path
import typer
import os
from datetime import datetime
import time

from ...core.env import load_config
from ...core.utils import info, run
from ...core.odoo_rpc import OdooRPC  # ✅ for optional post-update flush


def _module_exists_on_host(module: str, host_addons: str | None) -> bool:
    if not host_addons:
        return False
    p = Path(host_addons).expanduser().resolve() / module
    return p.is_dir()


def _module_exists_in_container(module: str, container: str) -> bool:
    # /mnt/extra-addons altında var mı?
    code, out, _ = run([
        "bash", "-lc",
        f"docker exec -i {shlex.quote(container)} sh -lc '[ -d /mnt/extra-addons/{shlex.quote(module)} ] && echo OK || true'"
    ])
    return (code == 0) and ("OK" in (out or ""))


def update(
    module: str = typer.Argument(..., help="Module name (e.g. opm_dev_helper)"),
    db: str = typer.Option(None, "--db", "-d", help="Database name (fallback: runtime.db)"),
    container: str = typer.Option(None, "--container", "-c", help="Docker container name for Odoo (use `docker ps`)"),
    addons: str = typer.Option(None, "--addons", help="Host addons path (fallback: runtime.addons[0])"),
    extra_ports: bool = typer.Option(True, "--extra-ports/--no-extra-ports", help="Avoid port clashes by using 8070+"),
    debug: bool = typer.Option(False, "--debug", help="Enable Odoo debug logging"),
    no_tty: bool = typer.Option(False, "--no-tty", help="Disable TTY for docker exec (use -i instead of -it)"),
    reload_after: bool = typer.Option(True, "--reload/--no-reload", help="After successful update: flush caches & signal browser reload"),
):
    """
    Update (install or upgrade) a single Odoo module without running tests.
    """

    cfg = load_config()
    info("[opm] 🧪 Starting update run…")
    container = container or cfg.get("runtime", "container")
    db = db or cfg.get("runtime", "db") or "odoo"

    info(f"[opm] Target DB: {db}")
    info(f"[opm] Target container: {container or 'LOCAL (odoo in PATH)'}")

    db_host = cfg.get("runtime", "db_host") or ""
    db_port = cfg.get("runtime", "db_port") or ""
    db_user = cfg.get("runtime", "db_user") or ""
    db_password = cfg.get("runtime", "db_password") or ""

    db_args = []
    if db_host:     db_args += [f"--db_host={db_host}"]
    if db_port:     db_args += [f"--db_port={db_port}"]
    if db_user:     db_args += [f"--db_user={db_user}"]
    if db_password: db_args += [f"--db_password={db_password}"]

    if db_host or db_port or db_user or db_password:
        info(f"[opm] DB conn: host={db_host or '-'} port={db_port or '-'} user={db_user or '-'}")

    # Resolve addons path (host)
    host_addons = addons
    if not host_addons:
        rta = cfg.get("runtime", "addons") or []
        if rta:
            host_addons = str(Path(rta[0]).expanduser().resolve())

    info(f"[opm] Host addons: {host_addons or '(not provided)'}")

    # --- preflight module existence check ---
    found_locally = _module_exists_on_host(module, host_addons)
    found_in_container = False
    if container:
        try:
            found_in_container = _module_exists_in_container(module, container)
        except Exception:
            found_in_container = False

    if not (found_locally or found_in_container):
        info(
            f"❌ Module '{module}' not found under any addons path.\n"
            f"   Checked host: {host_addons or '(unset)'}\n"
            f"   Checked container: /mnt/extra-addons/{module} (container={container or 'N/A'})\n"
            f"   Hints:\n"
            f"   • Ensure runtime.addons points to the folder that contains '{module}/'.\n"
            f"   • If running in Docker, bind-mount that folder to /mnt/extra-addons.\n"
            f"   • Or pass --addons /path/to/addons explicitly."
        )
        raise typer.Exit(2)

    # Build addons-path (inside container)
    addons_path = "/usr/lib/python3/dist-packages/odoo/addons"
    if host_addons:
        # assumes your compose mounts host_addons -> /mnt/extra-addons
        addons_path = f"{addons_path},/mnt/extra-addons"

    info(f"[opm] In-container addons-path: {addons_path}")
    info("[opm] Install/Upgrade mode: auto (-i & -u)")

    # --- Build Odoo command ---
    wrapped = None
    container_log = None  # only set if container

    if container:
        info("[opm] Detecting Odoo binary inside the container…")
        # Detect odoo binary inside the container (odoo or odoo-bin)
        code, out, err = run([
            "bash", "-lc",
            f"docker exec -i {shlex.quote(container)} sh -lc 'command -v odoo || command -v odoo-bin'",
        ])
        if code != 0 or not (out or "").strip():
            info(f"❌ No 'odoo' or 'odoo-bin' found in container: {container}")
            raise typer.Exit(1)
        odoo_bin = (out or "").strip()
        info(f"[opm] Odoo binary: {odoo_bin}")

        # Ports: Odoo 17+ doesn't support xmlrpc flags; http/longpolling only if desired
        if extra_ports:
            ports = "--http-port=8070 --longpolling-port=8071"
            info("[opm] Extra ports enabled: http=8070, longpolling=8071")
        else:
            ports = ""
            info("[opm] Extra ports disabled (using container defaults)")

        tty_flag = "-i" if no_tty else "-it"
        log_flag = "--log-level=debug" if debug else ""
        # For reliable log capture: write to file in container and copy back
        container_log = f"/tmp/opm_update_{int(time.time())}.log"
        log_file_flag = f"--logfile={container_log}"

        db_args_str = " ".join(db_args)
        cmd = f"""docker exec {tty_flag} {shlex.quote(container)} {shlex.quote(odoo_bin)} -d {shlex.quote(db)} \
                  -i {shlex.quote(module)} -u {shlex.quote(module)} --stop-after-init \
                  --addons-path={shlex.quote(addons_path)} {db_args_str} {ports} {log_flag} {log_file_flag}"""

        artifacts_dir = Path(".opm/artifacts")
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        host_log = artifacts_dir / "update_last.log"

        # Copy container log back even if command fails; return real exit code
        wrapped = (
            f"{cmd}; ec=$?; "
            f"docker cp {shlex.quote(container)}:{shlex.quote(container_log)} {shlex.quote(str(host_log.resolve()))} >/dev/null 2>&1 || true; "
            f"exit $ec"
        )
    else:
        # bare-metal fallback (expects `odoo` in PATH)
        db_args_str = " ".join(db_args)
        extra_log = " --log-level=debug" if debug else ""
        cmd = f"""stdbuf -oL -eL odoo -d {shlex.quote(db)} -i {shlex.quote(module)} -u {shlex.quote(module)} \
                  --stop-after-init --addons-path={shlex.quote(addons_path)} {db_args_str} --logfile=-{extra_log}"""

        artifacts_dir = Path(".opm/artifacts")
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        host_log = artifacts_dir / "update_last.log"
        # Pipe stdout/stderr to host_log; preserve exit code
        wrapped = f"{{ {cmd}; }} | tee {shlex.quote(str(host_log.resolve()))}; exit ${{PIPESTATUS[0]}}"

    # --- Execute ---
    info("[opm] ▶️  Executing update command…")
    info(f"[opm] Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    t0 = time.time()

    # redacted preview (do not leak db password in logs)
    redacted_cmd = wrapped
    if db_password:
        redacted_cmd = redacted_cmd.replace(f"--db_password={db_password}", "--db_password=******")

    if no_tty:
        info("[opm] no-tty mode active (docker exec -i; stdout/stderr will be captured)")

    code, out, err = run(["bash", "-lc", wrapped])
    info(f"[opm] ⏱️  Duration: {time.time() - t0:.1f}s")

    if code != 0:
        info("❌ Update failed. Command (redacted):")
        print(redacted_cmd)
        info("Last lines:")
        tail = (out or err or "").splitlines()[-80:]
        if not tail and host_log.exists():
            try:
                tail = host_log.read_text(errors="ignore").splitlines()[-200:]
            except Exception:
                tail = []
        print("\n".join(tail))
        info(f"[opm] 📄 Full log: {host_log}")
        raise typer.Exit(code)

    info("✅ Update finished successfully.")
    
    # Optional: post-update flush via RPC (best-effort)
    if reload_after:
        try:
            rt = {
                "odoo_url": cfg.get("runtime", "odoo_url"),
                "db":       cfg.get("runtime", "db"),
                "user":     cfg.get("runtime", "user"),
                "pass":     cfg.get("runtime", "pass"),
            }
            if rt["odoo_url"] and rt["db"] and rt["user"]:
                rpc = OdooRPC(rt["odoo_url"], rt["db"], rt["user"], rt["pass"])
                try:
                    rpc.login()
                    rpc.call("opm.dev.tools", "flush_caches")
                    info("[opm] Post-update: caches flushed via RPC.")
                except Exception as e:
                    info(f"[opm] Post-update: flush skipped ({e})")
        except Exception as e:
            info(f"[opm] Post-update: RPC init failed ({e})")

        # Notify dev WebSocket (for live reload)
        try:
            import asyncio
            import websockets  # type: ignore
            ws_host = (cfg.get("runtime", "ws_host") or "127.0.0.1")
            try:
                ws_port = int(cfg.get("runtime", "ws_port") or 8765)
            except Exception:
                ws_port = 8765

            async def _notify_reload():
                uri = f"ws://{ws_host}:{ws_port}"
                try:
                    async with websockets.connect(uri, ping_interval=None) as ws:
                        await ws.send("reload")
                        info(f"[opm] Notified dev WebSocket at {uri}")
                except Exception as e:
                    info(f"[opm] WS notify failed: {e}")

            asyncio.run(_notify_reload())
        except Exception:
            pass