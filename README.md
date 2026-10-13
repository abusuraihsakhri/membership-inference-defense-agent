# Membership Inference Defense Agent

A Python reference application for **rule-based operational audits**, with a FastAPI interface, a command-line batch evaluator, and a standalone browser preview.

**Scope:** Despite the repository name, the current implementation does **not** train shadow models, estimate membership-inference attack success, evaluate precision–recall or ROC curves, implement differential privacy, or provide a formal privacy guarantee. The existing thresholds are application-defined demonstration rules, not validated clinical or privacy-risk cutoffs.

## Interfaces

- **Standalone browser preview:** Open `web/index.html` in a modern browser. Select *Local preview* for calculations that remain in the current browser tab. No installation, server, external fonts, or Python runtime is needed.
- **Primary API:** Run `python cli.py serve --host 127.0.0.1 --port 8000` and open `http://127.0.0.1:8000/`. The browser's *Server audit* mode calls the same-origin `POST /api/audit` endpoint. API documentation is available at `/docs`.
- **Primary CLI:** `python cli.py audit`, `python cli.py batch -i sample.csv -o results.csv`, `python cli.py chat "status"`, and `python cli.py verify-audit`.
- **Legacy implementation:** `python -m mia_defense.cli audit` and `python -m mia_defense.cli serve` use a separate coordinator and thresholds. Results are **not interchangeable** with the primary API.

The browser preview follows the **primary** worker thresholds: primary metric >25, secondary metric >12, and a critical flag that elevates to critical. The descriptor keywords `DISCORDANT`, `ANOMALY`, `MUTANT`, `VIOLATION`, `FAIL`, or `REJECT` trigger a warning. These arbitrary operational rules are not derived from membership-inference theory. The legacy `mia_defense` path uses a secondary threshold of 10 instead of 12.

## Install and run

Requires Python 3.9 or later; CI exercises Python 3.10–3.12.

```bash
git clone https://github.com/abusuraihsakhri/membership-inference-defense-agent.git
cd membership-inference-defense-agent
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
python -m pytest -q
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2
python cli.py batch -i sample.csv -o results.csv
python cli.py serve --host 127.0.0.1 --port 8000
```

On Windows, activate with `.venv\Scripts\activate`. A legacy installed command is `membership-inference-defense-engine`; the primary installed command is `membership-inference-defense-agent`.

### API examples

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/api/audit \
  -H "Content-Type: application/json" \
  -d '{"task_id":"DEMO-1","target_identifier":"KEY-01","primary_metric":28.5,"secondary_metric":14.2,"status_descriptor":"NOMINAL"}'
```

The primary API also exposes `POST /api/chat` (deterministic mock), `GET /api/audit/logs` (in-process audit-chain metadata), and `GET /metrics` (JSON counters, **not** a Prometheus text exporter). For the authoritative request and response schema, use the running service's `/openapi.json`.

## Privacy and security boundaries

- **Browser local preview:** Inputs and results stay in the browser tab and are not sent to an API. No cryptographic audit signature is generated; counters reset on reload.
- **Server audit:** Submitted values reach the local FastAPI process. Screening rejects selected patterns (e.g. email addresses, SSNs, MRN formats), including patterns found in metadata. These regular expressions are **not comprehensive de-identification** and do **not** establish HIPAA Safe Harbor or GDPR compliance. Do not submit real patient information.
- **Audit records:** The primary server signs an in-memory hash chain with HMAC-SHA256. This is tamper-evident for a running process with a protected key, but is **not** durable or externally anchored. Records and task registries are lost on restart. `verify-audit` in a new CLI process verifies only that process's in-memory records (usually zero).
- **Keys:** For server deployments, set a strong `AUDIT_SECRET_KEY` through the environment. Without it, an ephemeral random key is created at process start. Do not store keys in the repository.
- **Access control:** The sample API does **not** implement user authentication or authorization. Bind to localhost unless you have supplied an independent security boundary and reviewed your deployment.

`MODEL_PROVIDER` is documented in `.env.example`, but only the deterministic local mock adapter is implemented; external Ollama, OpenAI, and Claude calls are **not** supported. The enrichment modules demonstrate placeholder rule evaluations, not their titled scientific algorithms.

## Testing and deployment

```bash
python -m pytest -q
python -m compileall -q agents mia_defense cli.py enrichment.py simulator.py
python simulator.py 100
docker build -t membership-inference-defense-agent .
```

GitHub Actions installs the package and runs Python tests and a JavaScript syntax check. The `web/` directory is self-contained and suitable for static hosting; the Pages deployment workflow publishes that directory when GitHub Pages is enabled and configured for Actions. Static hosting runs **local previews only**; it cannot run the Python/FastAPI API.

The Dockerfile runs the primary FastAPI service on port 8000. `docker-compose.yml` requires `AUDIT_SECRET_KEY` in a local `.env`.

## Project layout

`agents/` — primary rule workers, PHI-pattern guard, supervisor, mock adapter, and API.

`mia_defense/` — separate legacy rule coordinator, CLI, and API.

`enrichment.py` — placeholder enrichment evaluations; `tests/` — regression and module tests; `web/index.html` — standalone preview and optional same-origin API frontend.

## Compatibility and license

The browser preview uses standard JavaScript, HTML, and CSS; test with a current Chrome, Firefox, Safari, or Edge release. The backend requires Python and cannot execute directly on GitHub Pages.

MIT License — see [LICENSE](LICENSE).
