from __future__ import annotations
import subprocess, shlex, os, sys
from pathlib import Path
from typing import List, Tuple

def run(cmd: List[str], cwd: str|None=None, env: dict|None=None) -> Tuple[int, str, str]:
    proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate()
    return proc.returncode, out, err

def ensure_artifacts():
    Path(".opm/artifacts").mkdir(parents=True, exist_ok=True)

def info(msg: str):
    print(f"[opm] {msg}")

def which(bin_name: str) -> str|None:
    from shutil import which as _which
    return _which(bin_name)