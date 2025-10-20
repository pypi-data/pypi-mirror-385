from __future__ import annotations
from .env import Config
from .utils import run, info
from pathlib import Path
import os, json, tempfile

COMPOSE_TEMPLATE = """
services:
  db:
    image: {pg_image}
    environment:
      POSTGRES_DB: odoo
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
  odoo:
    image: {odoo_image}
    depends_on: [db]
    environment:
      HOST: db
      USER: odoo
      PASSWORD: odoo
    command: ["odoo", "--test-enable", "--stop-after-init"]
    volumes:
{mounts}
"""

def _mounts_yaml(mounts):
    lines = []
    for m in mounts:
        lines.append(f"      - {m}")
    return "\n".join(lines) if lines else "      - ./addons:/mnt/extra-addons:ro"

def compose_up_for_tests(cfg: Config) -> str:
    pg_image = cfg.get("docker","postgres_image")
    odoo_image = cfg.get("docker","odoo_image")
    mounts = cfg.get("docker","mounts", default=[])
    yml = COMPOSE_TEMPLATE.format(pg_image=pg_image, odoo_image=odoo_image, mounts=_mounts_yaml(mounts))
    tmpdir = tempfile.mkdtemp(prefix="opm-")
    compose_file = os.path.join(tmpdir, "docker-compose.yml")
    with open(compose_file, "w", encoding="utf-8") as f:
        f.write("version: '3.8'\n" + yml)
    info(f"compose created at {compose_file}")
    code, out, err = run(["docker","compose","-f",compose_file,"up","-d"])
    if code != 0:
        raise RuntimeError("docker compose up failed: " + err)
    return compose_file

def compose_down(compose_file: str):
    run(["docker","compose","-f",compose_file,"down"])