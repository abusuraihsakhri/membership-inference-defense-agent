# Membership Inference Defense Agent

> **Domain:** Privacy-Preserving Healthcare & Federated Computing
> **Reference Guidelines & Standards:** `HIPAA Safe Harbor §164.514 & Differential Privacy RDP`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Membership Inference Defense Agent** is an advanced analytical and computational platform implementing Shadow model training & membership inference attack (MIA) risk estimation. It provides multi-worker consensus evaluation with cryptographic audit trails and PHI protection.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization with automated clinical/operational action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking and anomaly detection.
- **Multi-Worker Consensus**: InvariantQC, SafetyEscalation, and ProtocolConformance workers.

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/membership-inference-defense-agent.git
cd membership-inference-defense-agent

# Install dependencies
pip install -e .

# Or with test dependencies
pip install -e ".[test]"

# Configure environment (recommended for production)
cp .env.example .env
# Edit .env and set a secure AUDIT_SECRET_KEY
```

### Environment Variables

| Variable | Description | Default |
|:---------|:------------|:--------|
| `AUDIT_SECRET_KEY` | HMAC-SHA256 key for audit trail integrity | Random (ephemeral) |
| `MODEL_PROVIDER` | LLM provider (`mock`, `ollama`, `claude`, `openai`) | `mock` |

---

## 💻 CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2
```

### 2. Batch Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 3. System Query
```bash
python cli.py chat "What is the system status?"
```

### 4. Verify Audit Integrity
```bash
python cli.py verify-audit
```

### 5. Launch API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
- `--task-id`: Unique task/case identifier
- `--target`: Entity, patient key, or target identifier
- `--primary`: Primary domain measurement or score (float)
- `--secondary`: Secondary metric or confidence score (float)
- `--critical`: Flag for emergency escalation
- `--status`: Status code or phenotype descriptor

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Unique task identifier | Required |
| `target_identifier` | Target entity identifier | Required |
| `primary_metric` | Primary measurement value | Required |
| `secondary_metric` | Secondary measurement value | Optional |
| `is_critical_flag` | Emergency escalation flag | Optional |
| `status_descriptor` | Status/phenotype descriptor | Optional |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, DOBs, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs with signature verification for every evaluation and state transition.
* **Secure Key Management:** Audit keys configured via `AUDIT_SECRET_KEY` environment variable (no hardcoded secrets).
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

### Docker
```bash
docker build -t membership-inference-defense-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))") membership-inference-defense-agent
```

### Docker Compose
```bash
# Create .env file with required variables
echo "AUDIT_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" > .env

# Launch
docker-compose up -d
```

---

## 📁 Project Structure

```
membership-inference-defense-agent/
├── agents/                  # Core agent modules
│   ├── api.py              # FastAPI REST endpoints
│   ├── base.py             # Security, PHI guard, audit trail
│   ├── learning.py         # Bayesian calibration engine
│   ├── llm_factory.py      # LLM provider factory
│   ├── metrics.py          # Prometheus metrics collector
│   ├── models.py           # Pydantic data models
│   ├── streamer.py         # WebSocket telemetry
│   ├── supervisor.py       # Master orchestrator
│   └── workers.py          # Specialized worker agents
├── mia_defense/            # Alternative MIA defense implementation
│   ├── agents.py           # Sub-agents (shadow trainer, etc.)
│   ├── cli.py              # CLI entry point
│   ├── engine.py           # Core algorithmic engine
│   ├── models.py           # Data models
│   └── server.py           # FastAPI server factory
├── tests/                  # Test suite
│   ├── test_enrichment.py
│   ├── test_membership_inference_defense_agent.py
│   ├── test_mia_defense.py
│   └── test_security.py    # Security & edge case tests
├── web/index.html          # Operations console UI
├── cli.py                  # Top-level CLI entry point
├── simulator.py            # High-throughput simulation
├── enrichment.py           # Enrichment feature engines
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── LICENSE
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
