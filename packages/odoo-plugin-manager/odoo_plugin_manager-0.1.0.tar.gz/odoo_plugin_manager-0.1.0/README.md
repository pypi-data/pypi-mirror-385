# 🧩 OPM — Odoo Plugin Manager (CLI)

**OPM** is a modern and lightweight command-line tool for Odoo developers.
It streamlines development and testing by providing smart automation for cache refreshes,
module testing, and environment management — without restarting Odoo.

Designed for developers who want to work faster and cleaner with **Odoo 14 → 17+**.

---

## ⚙️ Installation

Install from PyPI:

```bash
pip install opm
```

---

## 📁 Configuration

When you first run OPM, it automatically creates an `opm.yaml` configuration file in your working directory.
This file defines your Odoo connection details and development environment.

Example:

```yaml
runtime:
  odoo_url: "http://localhost:10017"
  db: "main"
  user: "admin"
  pass: "admin"
  addons:
    - "/path/to/odoo/addons"
  container: "odoo17"
```

> OPM automatically reads this file for every command.
> No manual setup or environment variables required.

---

## 🚀 Commands

### 🪄 `opm init`

Initializes a new OPM project by generating a sample `opm.yaml` configuration file.
You can edit this file to match your Odoo environment (URL, DB, user, etc.).

```bash
opm init
```

Example output:

```
[opm] Creating opm.yaml configuration...
[opm] ✅ Configuration created successfully at ./opm.yaml
```

After running `opm init`, you can immediately start developing with:

```bash
opm dev
```

---

### 🔧 `opm dev`

Starts **development mode**, watching your Odoo addons directory for changes.
Whenever you modify an XML, JS, or QWeb file, OPM triggers an automatic cache flush through RPC —
instantly reflecting UI and view updates without restarting Odoo.

```bash
opm dev
```

Example output:

```
[opm] Connected to Odoo environment 'runtime'
[opm] Watching for changes in: /addons
[opm] Asset/template changed: queue_job/views/menu.xml → flush caches
```

> ⚠️ Note: This is **not full hot reload** — Python code changes still require a manual reload.
> XML, QWeb, and JS updates are applied live through Odoo’s cache system.

---

### 🧪 `opm test <module>`

Runs tests for the specified Odoo module.
If the module is not yet installed, OPM automatically installs or upgrades it before running tests.

```bash
opm test my_module
```

Example:

```
[opm] Odoo binary detected: /usr/bin/odoo
[opm] Running tests for module: my_module
✅ Tests finished successfully.
```

If something goes wrong:

```
❌ Tests failed. See .opm/artifacts/test_last.log for details.
```

All test outputs and logs are automatically saved to:

```
.opm/artifacts/
```

> The test command is ideal for CI/CD pipelines or quick module validation
> without manually launching Odoo.

---

### 🩺 `opm diagnose`

Runs a quick environment diagnostic to ensure OPM and Odoo are properly connected.

```bash
opm diagnose
```

Example output:

```
[opm] 🔍 Running environment diagnostics...
[opm] Docker CLI: ✅ Found
[opm] Odoo binary: ✅ Found (/usr/bin/odoo)
[opm] Testing Odoo URL: http://localhost:10017
[opm] ✅ Odoo instance reachable.
[opm] 🏁 Diagnose complete.
```

---

## 🧩 Features

| Feature                        | Description                                                         |
| ------------------------------ | ------------------------------------------------------------------- |
| ⚙️ **Automatic Cache Refresh** | Detects XML, QWeb, or JS changes and flushes Odoo caches instantly. |
| 🧪 **Module Install/Upgrade**  | Automatically installs or upgrades modules before running tests.    |
| 🗱 **Docker Integration**      | Detects and executes inside Odoo containers automatically.          |
| 📦 **Artifact Logging**        | Saves logs and test outputs under `.opm/artifacts/`.                |
| ⚡ **YAML Config System**       | Uses a single `opm.yaml` file for all environment details.          |
| 🧠 **RPC-Based Architecture**  | Works with Odoo via XML-RPC — no code injection or patching needed. |

---

## 🔮 Future Roadmap

These are upcoming features currently under development:

* 🔁 **Hot Reload** — true live reload support for Odoo front-end assets
* 🧩 **Advanced Helper Addon (`opm_dev_helper`)** — deeper cache and UI refresh controls
* 📊 **Improved Test Reporting** — detailed test result summaries and coverage integration

---

## 🧠 Technical Overview

| Key                    | Details                                             |
| ---------------------- | --------------------------------------------------- |
| **Language**           | Python 3.10+                                        |
| **Dependencies**       | typer, rich, watchdog, requests, pyyaml, websockets |
| **Odoo Compatibility** | 14 → 17+                                            |
| **Platforms**          | macOS / Linux                                       |
| **Configuration File** | `opm.yaml` (auto-created on first run)              |

---

## 🦦 Example Workflow

A simple developer workflow might look like this:

```bash
# 1️⃣ Initialize config
opm init

# 2️⃣ Check your setup
opm diagnose

# 3️⃣ Start development mode (watch for file changes)
opm dev

# 4️⃣ Run tests for your module
opm test my_module
```

This setup keeps your Odoo instance responsive
and your local development cycle short — no manual restarts needed.

---

## 📜 License

Licensed under the **GNU General Public License v3 (GPL-3.0-or-later)**.
The OPM CLI is open source.
Future Odoo-specific helper addons may be released under a separate commercial license.

---

© 2025 Ahmet Atakan — Crafted for real Odoo developers who build faster, smarter, and cleaner.
