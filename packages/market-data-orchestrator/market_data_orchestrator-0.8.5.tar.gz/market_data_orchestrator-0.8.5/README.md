<div align="center">

# 🎯 Market Data Orchestrator

**Production-ready orchestration service for real-time market data pipelines**

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Version](https://img.shields.io/badge/version-0.8.0-green)](https://github.com/mjdevaccount/market_data_orchestrator/releases/tag/v0.8.0)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![SOLID](https://img.shields.io/badge/SOLID-✓-success)](docs/ARCHITECTURE_OVERVIEW.md)

[Features](#-features) • [Quick Start](#-quick-start) • [API Documentation](#-api-documentation) • [Deployment](#-deployment) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#%EF%B8%8F-architecture)
- [Technology Stack](#%EF%B8%8F-technology-stack)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Configuration](#%EF%B8%8F-configuration)
- [Cockpit Dashboard](#%EF%B8%8F-cockpit-dashboard)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Monitoring & Observability](#-monitoring--observability)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Market Data Orchestrator** is a production-grade control service that coordinates and monitors real-time market data pipelines. Built with SOLID principles, it seamlessly integrates data providers, processing pipelines, and storage layers while providing comprehensive observability, control capabilities, and a web-based cockpit interface.

### What It Does

- **Orchestrates** data flow from providers (IBKR) → pipeline → store
- **Monitors** pipeline health and performance metrics via Prometheus
- **Controls** runtime behavior (pause/resume/reload) with audit logging
- **Secures** operations with JWT/OIDC authentication and RBAC
- **Federates** control commands across multi-region deployments
- **Provides** real-time web dashboard and WebSocket status streams

### Use Cases

- **Real-time market data ingestion** from Interactive Brokers
- **Multi-region pipeline orchestration** with federated control
- **Production monitoring** with Prometheus/Grafana integration
- **Graceful degradation** via pause/resume controls
- **Audit compliance** with persistent JSONL audit trails
- **Zero-downtime operations** with hot configuration reload

### What's New in v0.6.0 (Phase 8.0) 🆕

- ✅ **Core v1.1.0 Contract Adoption** - Standardized telemetry and federation contracts
- ✅ **Telemetry Contracts** - `HealthStatus`, `ControlResult`, `AuditEnvelope` from `market-data-core`
- ✅ **Federation Contracts** - `ClusterTopology`, `NodeStatus`, `FederationDirectory` protocol
- ✅ **Rich Topology** - Node roles, regions, health status for multi-orchestrator deployments
- ✅ **Zero Breaking Changes** - 100% backward compatible API upgrades

---

## ✨ Key Features

### Phase 8.0 - Core v1.1.0 Contracts (Latest) 🆕
- ✅ **Standardized Telemetry** - Core `HealthStatus` with component health breakdown
- ✅ **Control Contracts** - Core `ControlResult` and `AuditEnvelope` for audit compliance
- ✅ **Federation Topology** - Rich cluster topology with node IDs, roles, and regions
- ✅ **Protocol Conformance** - `FederationDirectory` protocol for extensible topology
- ✅ **Contract Tests** - Comprehensive schema validation and snapshot tests

### Phase 3 - SOLID Architecture
- ✅ **Dependency Injection** - `ServiceContainer` for proper DI and testability
- ✅ **Protocol-Based Abstractions** - `Provider`, `Runtime`, `FeedbackBus`, `RateLimiter`, `AuditLogger`
- ✅ **Focused Settings Groups** - ISP-compliant configuration (Runtime, Security, Provider, etc.)
- ✅ **Extensible Event System** - Plugin-based event handlers (OCP compliance)
- ✅ **Service Layer** - Specialized services (LifecycleManager, ControlPlane, StatusAggregator)

### Phase 6.3 - Security & Federation
- ✅ **JWT/OIDC Authentication** - Industry-standard token-based auth with JWKS verification
- ✅ **Role-Based Access Control (RBAC)** - Viewer, operator, and admin roles
- ✅ **Redis Rate Limiting** - Token-bucket algorithm with fail-open design
- ✅ **Persistent Audit Logging** - JSONL audit trail for all control actions
- ✅ **Multi-Pipeline Federation** - Forward control commands to peer orchestrators
- ✅ **Dual-Auth Transition** - Zero-downtime migration from API keys to JWT

### Phase 6.2 - Cockpit & Control Plane
- ✅ **Interactive Web Dashboard** - Real-time system status UI at `/ui`
- ✅ **WebSocket Status Stream** - Live updates every 2 seconds
- ✅ **Control Plane API** - Pause, resume, and reload runtime operations
- ✅ **Rate Limiting** - Redis-backed rate limiting (5 actions/minute)
- ✅ **Control Metrics** - Prometheus counters for all control actions

### Phase 6.1 - Core Orchestration
- ✅ **Unified Runtime Management** - Coordinates providers, pipelines, and storage
- ✅ **Feedback Bus Integration** - Subscribes to backpressure and health events
- ✅ **Health & Metrics APIs** - RESTful endpoints for service status
- ✅ **Prometheus Integration** - Native metrics export for monitoring
- ✅ **Graceful Shutdown** - SIGINT/SIGTERM handling with cleanup

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Market Data Orchestrator v0.6.0                    │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    ServiceContainer (DI)                       │  │
│  │  • Provider, Runtime, FeedbackBus, RateLimiter, AuditLogger   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              │                                        │
│  ┌───────────────────────────┴───────────────────────────────────┐  │
│  │                  FastAPI Application                           │  │
│  │                                                                 │  │
│  │  REST APIs                WebSocket           Control Plane    │  │
│  │  • /health → HealthStatus  • /ws/status       • /control/*     │  │
│  │  • /status                 • Live updates     • JWT/RBAC       │  │
│  │  • /metrics                • 2s interval      • Audit logging  │  │
│  │  • /federation/topology                       • Rate limiting  │  │
│  │                                                                 │  │
│  │  Static UI                Federation                           │  │
│  │  • /ui (Cockpit)          • /federation/topology → ClusterTopo │  │
│  │  • Dashboard              • /federation/forward/{peer}         │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                              │                                        │
│  ┌───────────────────────────┴───────────────────────────────────┐  │
│  │             Orchestrator (Facade Pattern)                      │  │
│  │                                                                 │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │  │
│  │  │  Lifecycle   │  │ ControlPlane │  │ StatusAggregator │    │  │
│  │  │   Manager    │  │   Service    │  │                  │    │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘    │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                              │                                        │
│            ┌─────────────────┼─────────────────┐                     │
│            │                 │                 │                      │
│            ▼                 ▼                 ▼                      │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│    │UnifiedRuntime│  │ FeedbackBus  │  │IBKRProvider  │            │
│    │  (Pipeline)  │  │   (Redis)    │  │              │            │
│    └──────────────┘  └──────────────┘  └──────────────┘            │
└───────────┬───────────────────┬─────────────────┬───────────────────┘
            │                   │                 │
            ▼                   ▼                 ▼
    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
    │   Pipeline   │    │  Redis Store │    │ IBKR Gateway │
    │  Operators   │    │  + Feedback  │    │   (TWS/IB    │
    │              │    │     Bus      │    │   Gateway)   │
    └──────────────┘    └──────────────┘    └──────────────┘
            │
            ▼
    ┌──────────────┐
    │ Prometheus   │
    │  + Grafana   │
    └──────────────┘
```

### Core Principles

**SOLID Architecture (Phases 1-3):**
- ✅ **Single Responsibility** - Each service has one clear purpose
- ✅ **Open/Closed** - Extensible via protocols without modifying core
- ✅ **Liskov Substitution** - Protocol implementations are substitutable
- ✅ **Interface Segregation** - Focused settings groups (Runtime, Security, etc.)
- ✅ **Dependency Inversion** - ServiceContainer with protocol abstractions

**Contract-First Design (Phase 8.0):**
- Import from `market-data-core.*` only; no shadow DTOs
- Additive changes; deprecate before removal
- Clear separation: Core = contracts; repos = implementations
- Fail-open where safe (telemetry/audit), fail-closed for auth/controls

### Component Flow

1. **ServiceContainer** - Centralized dependency injection
2. **FastAPI App** - Exposes REST/WebSocket APIs, serves UI
3. **Orchestrator** - Facade delegating to specialized services
4. **LifecycleManager** - Manages component start/stop/cleanup
5. **ControlPlaneService** - Handles pause/resume/reload with audit
6. **StatusAggregator** - Collects system status from all components
7. **UnifiedRuntime** - Manages pipeline execution (from `market-data-pipeline`)
8. **FeedbackBus** - Handles backpressure and health events (from `market-data-store`)
9. **IBKRProvider** - Connects to Interactive Brokers TWS/Gateway

---

## 🛠️ Technology Stack

### Core Technologies
- **Python 3.11+** - Modern async/await support
- **FastAPI 0.104+** - High-performance async web framework
- **AsyncIO** - Concurrent event-driven architecture
- **Pydantic 2.0+** - Data validation and settings management
- **Uvicorn** - Lightning-fast ASGI server with WebSocket support

### Market Data Integration Layer
- **market-data-core v1.1.0** - Shared contracts and telemetry types
- **market-data-pipeline v0.8.1** - UnifiedRuntime execution engine
- **market-data-store v0.3.0** - Storage and feedback bus
- **market-data-ibkr v1.0.0** - Interactive Brokers provider

### Security & Authentication
- **python-jose** - JWT/OIDC token verification
- **Redis 5.0+** - Rate limiting and feedback bus
- **JWKS** - Cryptographic key verification

### Observability
- **Prometheus Client** - Metrics collection and export
- **Grafana** - Visualization (via Prometheus metrics)
- **Structured Logging** - JSON/text format support

### Deployment
- **Docker** - Containerized deployment
- **Kubernetes** - Production orchestration
- **HTTPX** - Async HTTP client for federation

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** installed
- **Redis** (optional, for feedback bus and rate limiting)
- **Interactive Brokers TWS/Gateway** (for live data)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/mjdevaccount/market_data_orchestrator.git
cd market_data_orchestrator

# 2. Create virtual environment
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Unix/macOS/Linux
source .venv/bin/activate

# 3. Install package
pip install -e .

# Install with dev dependencies (for testing/linting)
pip install -e ".[dev]"
```

### Basic Usage

```bash
# 1. Set required environment variables
export ORCH_API_KEY="your-secure-api-key"  # For control endpoints
export ORCH_FEEDBACK_URL="redis://localhost:6379/0"

# 2. Start the orchestrator
python -m market_data_orchestrator.launcher

# Expected output:
# INFO: API server starting (v0.6.0)
# INFO: ServiceContainer initialized
# INFO: WebSocket broadcast task started
# INFO: Orchestrator running
# INFO: Uvicorn running on http://0.0.0.0:8080
```

### Verify Installation

```bash
# Health check (returns Core HealthStatus)
curl http://localhost:8501/health

# Expected response:
# {
#   "service": "orchestrator",
#   "state": "healthy",
#   "components": [
#     {"name": "provider", "state": "healthy"},
#     {"name": "runtime", "state": "healthy"},
#     {"name": "websocket", "state": "healthy"},
#     {"name": "feedback_bus", "state": "healthy"}
#   ],
#   "version": "0.6.0",
#   "ts": 1729197600.0
# }

# View Prometheus metrics
curl http://localhost:8501/metrics

# Access web dashboard
open http://localhost:8501/ui

# Get cluster topology (Phase 8.0)
curl http://localhost:8501/federation/topology

# Expected response:
# {
#   "cluster_id": {"value": "default"},
#   "region": {"name": "local"},
#   "nodes": [
#     {
#       "node_id": {"value": "orchestrator-local"},
#       "role": "orchestrator",
#       "health": "healthy",
#       "version": "0.6.0",
#       "last_seen_ts": 1729197600.0
#     }
#   ]
# }
```

---

## 📡 API Documentation

### REST Endpoints

#### Health & Status

| Endpoint | Method | Auth | Response Model | Description |
|----------|--------|------|----------------|-------------|
| `/health` | GET | None | `HealthStatus` | Service health check (Core v1.1.0 contract) |
| `/status` | GET | None | JSON | Detailed orchestrator status snapshot |
| `/metrics` | GET | None | Text | Prometheus metrics in text format |

**Example:**
```bash
curl http://localhost:8501/health

# Response (Core v1.1.0 HealthStatus):
{
  "service": "orchestrator",
  "state": "healthy",
  "components": [
    {"name": "provider", "state": "healthy", "detail": "Connected to IBKR"},
    {"name": "runtime", "state": "healthy", "detail": "Pipeline running"},
    {"name": "websocket", "state": "healthy", "detail": "2 clients connected"},
    {"name": "feedback_bus", "state": "healthy", "detail": "Redis connected"}
  ],
  "version": "0.6.0",
  "ts": 1729197600.0
}
```

#### Authentication

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/auth/ping` | GET | API Key or JWT | Test authentication validity |

**Example:**
```bash
# API Key authentication
curl -H "X-API-Key: your-api-key" http://localhost:8501/auth/ping

# JWT authentication
curl -H "Authorization: Bearer eyJhbGc..." http://localhost:8501/auth/ping

# Response:
{"status": "ok", "user": "operator@example.com", "role": "operator"}
```

#### Control Plane (JWT/RBAC Protected)

| Endpoint | Method | Auth | Role | Response Model | Description |
|----------|--------|------|------|----------------|-------------|
| `/control/pause` | POST | JWT/API Key | Operator+ | `ControlResult` | Pause data ingestion (soft stop) |
| `/control/resume` | POST | JWT/API Key | Operator+ | `ControlResult` | Resume data ingestion |
| `/control/reload` | POST | JWT/API Key | Admin | `ControlResult` | Reload configuration (hot reload) |

**Example:**
```bash
# Pause ingestion (JWT)
curl -X POST \
  -H "Authorization: Bearer eyJhbGc..." \
  http://localhost:8501/control/pause

# Response (Core v1.1.0 ControlResult):
{
  "status": "ok",
  "detail": "Orchestrator paused"
}

# Resume ingestion (API Key)
curl -X POST \
  -H "X-API-Key: your-api-key" \
  http://localhost:8501/control/resume

# Response:
{
  "status": "ok",
  "detail": "Orchestrator resumed"
}
```

**Rate Limiting:**
- Control endpoints are rate-limited to **5 actions per minute** per action type
- Redis-backed with fail-open design
- Exceeding the limit returns `HTTP 429 Too Many Requests`

#### Federation (Phase 8.0)

| Endpoint | Method | Auth | Response Model | Description |
|----------|--------|------|----------------|-------------|
| `/federation/topology` | GET | JWT/API Key | `ClusterTopology` | Get cluster topology with node roles and regions |
| `/federation/list` | GET | JWT/API Key | JSON | Legacy endpoint (deprecated, use `/topology`) |
| `/federation/forward/{peer}` | POST | JWT (Admin) | JSON | Forward control command to peer orchestrator |

**Example:**
```bash
# Get cluster topology (Core v1.1.0)
curl -H "Authorization: Bearer eyJhbGc..." \
  http://localhost:8501/federation/topology

# Response (ClusterTopology):
{
  "cluster_id": {"value": "production"},
  "region": {"name": "us-east"},
  "nodes": [
    {
      "node_id": {"value": "mdp-us"},
      "role": "pipeline",
      "health": "healthy",
      "version": "0.9.0",
      "last_seen_ts": 1729197600.0
    },
    {
      "node_id": {"value": "mds-eu"},
      "role": "store",
      "health": "healthy",
      "version": "0.4.0",
      "last_seen_ts": 1729197590.0
    }
  ]
}
```

### WebSocket Stream

#### `/ws/status` - Real-Time Status Updates

Broadcasts orchestrator status every 2 seconds to all connected clients.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8501/ws/status');

ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Status update:', message);
};
ws.onerror = (error) => console.error('WebSocket error:', error);
```

**Message Format:**
```json
{
  "type": "status",
  "data": {
    "service": "market-data-orchestrator",
    "running": true,
    "paused": false,
    "runtime": {
      "state": "running",
      "mode": "dag"
    },
    "feedback": "connected",
    "version": "0.6.0"
  }
}
```

### Static Assets

| Endpoint | Description |
|----------|-------------|
| `/ui` | Cockpit dashboard (HTML/JavaScript UI) |
| `/ui/cockpit.js` | Dashboard JavaScript |

---

## ⚙️ Configuration

All configuration is via **environment variables** with the `ORCH_` prefix.

### Core Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ORCH_API_KEY` | **Yes** (prod) | `""` | API key for control endpoints (fallback auth) |
| `ORCH_RUNTIME_MODE` | No | `dag` | Pipeline execution mode: `dag`, `streaming`, `batch` |
| `ORCH_FEEDBACK_URL` | No | `redis://localhost:6379/0` | Redis URL for feedback bus |
| `ORCH_FEEDBACK_ENABLED` | No | `true` | Enable/disable feedback event subscription |

### Provider Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ORCH_PROVIDER_HOST` | No | `127.0.0.1` | IBKR TWS/Gateway host |
| `ORCH_PROVIDER_PORT` | No | `7497` | IBKR TWS/Gateway port (`7497` TWS, `4001` Gateway) |
| `ORCH_PROVIDER_CLIENT_ID` | No | `1` | IBKR client identifier |

### API Server Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ORCH_HEALTH_HOST` | No | `0.0.0.0` | FastAPI server bind address |
| `ORCH_HEALTH_PORT` | No | `8080` | FastAPI server port |
| `ORCH_WS_INTERVAL_SEC` | No | `2.0` | WebSocket broadcast interval (seconds) |

### Logging Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ORCH_LOG_LEVEL` | No | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `ORCH_LOG_FORMAT` | No | `json` | Log output format: `json` or `text` |

### Security & Authentication (Phase 6.3)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| **JWT/OIDC Authentication** ||||
| `ORCH_JWT_ENABLED` | No | `false` | Enable JWT/OIDC authentication |
| `ORCH_OIDC_ISSUER` | **Yes** (if JWT) | `""` | OIDC issuer URL (e.g., `https://tenant.auth0.com/`) |
| `ORCH_OIDC_AUDIENCE` | **Yes** (if JWT) | `market-data-orchestrator` | JWT audience claim (client ID) |
| `ORCH_JWKS_URL` | **Yes** (if JWT) | `""` | JWKS endpoint for token verification |
| `ORCH_JWT_ROLE_CLAIM` | No | `roles` | JWT claim name containing user roles |
| `ORCH_JWT_CACHE_TTL` | No | `3600` | JWKS cache TTL in seconds |
| `ORCH_DUAL_AUTH` | No | `true` | Allow both JWT and API key during transition |
| **Rate Limiting** ||||
| `ORCH_REDIS_RATE_LIMIT_URL` | No | `redis://localhost:6379/1` | Redis URL for rate limiting (DB 1) |
| `ORCH_RATE_LIMIT_ENABLED` | No | `true` | Enable Redis-backed rate limiting |
| `ORCH_RATE_LIMIT_MAX_PER_MINUTE` | No | `5` | Max control actions per minute per type |
| **Audit Logging** ||||
| `ORCH_AUDIT_LOG_PATH` | No | `logs/audit.jsonl` | Path to audit log file (JSONL format) |
| `ORCH_AUDIT_LOG_ENABLED` | No | `true` | Enable persistent audit logging |
| **Federation** ||||
| `ORCH_FEDERATION_PEERS` | No | `""` | Comma-separated peer URLs (e.g., `http://mdp-us:8080,http://mdp-eu:8080`) |

> **📚 For detailed OIDC setup:** See [`docs/PHASE_6.3_OIDC_SETUP.md`](docs/PHASE_6.3_OIDC_SETUP.md)

### Example `.env` File

```bash
# === Phase 8.0: Core v1.1.0 Contracts ===
# (No new config required - all handled via imports)

# === Phase 6.3: JWT/OIDC Authentication (Production) ===
ORCH_JWT_ENABLED=true
ORCH_OIDC_ISSUER=https://YOUR_TENANT.auth0.com/
ORCH_OIDC_AUDIENCE=market-data-orchestrator
ORCH_JWKS_URL=https://YOUR_TENANT.auth0.com/.well-known/jwks.json
ORCH_DUAL_AUTH=true  # Allow both JWT and API key during migration

# === API Key (Fallback/Development) ===
ORCH_API_KEY=your-secure-random-key-here

# === Phase 6.3: Redis Rate Limiting ===
ORCH_REDIS_RATE_LIMIT_URL=redis://localhost:6379/1
ORCH_RATE_LIMIT_ENABLED=true
ORCH_RATE_LIMIT_MAX_PER_MINUTE=5

# === Phase 6.3: Audit Logging ===
ORCH_AUDIT_LOG_PATH=logs/audit.jsonl
ORCH_AUDIT_LOG_ENABLED=true

# === Phase 6.3: Federation (Multi-Region) ===
ORCH_FEDERATION_PEERS=http://orchestrator-us:8080,http://orchestrator-eu:8080

# === Runtime Configuration ===
ORCH_RUNTIME_MODE=dag
ORCH_FEEDBACK_ENABLED=true
ORCH_FEEDBACK_URL=redis://localhost:6379/0

# === Provider Configuration ===
ORCH_PROVIDER_HOST=127.0.0.1
ORCH_PROVIDER_PORT=7497
ORCH_PROVIDER_CLIENT_ID=1

# === API Server Configuration ===
ORCH_HEALTH_HOST=0.0.0.0
ORCH_HEALTH_PORT=8080
ORCH_WS_INTERVAL_SEC=2.0

# === Logging ===
ORCH_LOG_LEVEL=INFO
ORCH_LOG_FORMAT=json
```

---

## 🎛️ Cockpit Dashboard

### Overview

The **Cockpit Dashboard** is a real-time web interface for monitoring and controlling the orchestrator.

**Access:** http://localhost:8501/ui

### Features

- ✅ **Live Status Display** - WebSocket-powered real-time updates (2s interval)
- ✅ **Connection Configuration** - Set API base URL and authentication
- ✅ **Control Buttons** - Pause, resume, and reload with one click
- ✅ **Status Visualization** - JSON viewer for current system state
- ✅ **Persistent Config** - Settings stored in browser localStorage

### Usage

1. **Open Dashboard**
   ```bash
   open http://localhost:8501/ui
   ```

2. **Configure Connection**
   - **API Base URL**: `http://localhost:8501` (auto-filled)
   - **API Key**: Enter your `ORCH_API_KEY` value (or leave empty for JWT)
   - Click **Save**

3. **Monitor Status**
   - WebSocket connection status displayed at top
   - Status box updates every 2 seconds
   - Shows `running`, `paused`, `runtime` state, component health

4. **Control Operations** (requires Operator/Admin role)
   - **Pause** - Stops data ingestion (soft pause)
   - **Resume** - Restarts data ingestion
   - **Reload** - Hot-reloads configuration (Admin only)

### Security Note

⚠️ **Development Only**: The UI stores API keys in browser `localStorage`. For production deployments, use JWT/OIDC authentication with httpOnly cookies or server-side sessions.

---

## 🧪 Testing

### Run All Tests

```bash
# Windows PowerShell
$env:PYTHONPATH="$PWD\src"

# Unix/macOS/Linux
export PYTHONPATH="$PWD/src"

# Run all tests
pytest -v

# Run with coverage
pytest --cov=market_data_orchestrator --cov-report=html --cov-report=term

# View coverage report
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS/Linux
```

### Test Suites

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Contract tests (Phase 8.0)
pytest tests/api/test_health_contract.py -v
pytest tests/api/test_control_audit_contract.py -v
pytest tests/api/test_federation_contract.py -v
pytest tests/api/test_schemas.py -v

# Specific test file
pytest tests/test_auth_jwt.py -v

# Specific test function
pytest tests/test_control.py::test_pause_resume_cycle -v
```

### Test Coverage

- **Unit Tests**: 25+ tests (settings, lifecycle, services, protocols)
- **Integration Tests**: 8+ tests (E2E flows, feedback events)
- **API Tests**: 20+ tests (auth, control endpoints, rate limiting, federation)
- **Contract Tests**: 15+ tests (Core v1.1.0 schema validation)
- **Total Coverage**: > 85% line coverage

### Contract Testing (Phase 8.0)

Phase 8.0 introduces contract tests to ensure compliance with Core v1.1.0 schemas:

```bash
# Run contract tests
pytest tests/api/test_health_contract.py -v
pytest tests/api/test_control_audit_contract.py -v
pytest tests/api/test_federation_contract.py -v
pytest tests/services/test_federation_directory.py -v
pytest tests/api/test_schemas.py -v

# Example: test health endpoint returns Core HealthStatus
def test_health_returns_core_healthstatus_schema(jwt_client, mock_jwt_token):
    response = await jwt_client.get("/health")
    health_status = HealthStatus(**response.json())
    assert health_status.service == "orchestrator"
    assert health_status.state in ["healthy", "degraded", "unhealthy"]
```

---

## 🐳 Deployment

### Docker Compose (Recommended)

**The orchestrator is fully integrated with the unified `market_data_infra` compose-based infrastructure.**

📚 **See [DOCKER_COMPOSE_INTEGRATION.md](DOCKER_COMPOSE_INTEGRATION.md) for complete setup instructions.**

Quick start from `market_data_infra` repository:

```bash
# Start full stack
make up-orchestrator

# Or with docker compose directly
docker compose --profile infra --profile core --profile store --profile pipeline --profile orchestrator up -d

# Check health
curl http://localhost:8501/health
```

### Docker (Standalone)

#### Build Image

```bash
docker build -f deploy/Dockerfile -t market-data-orchestrator:0.8.0 .
```

#### Run Container

```bash
# With environment file
docker run -p 8501:8501 --env-file .env market-data-orchestrator:0.8.0

# With inline environment variables
docker run -p 8501:8501 \
  -e ORCH_FEEDBACK_URL=redis://redis:6379/0 \
  -e ORCH_JWT_ENABLED=true \
  -e ORCH_OIDC_ISSUER=https://tenant.auth0.com/ \
  market-data-orchestrator:0.8.0

# Run in background
docker run -d -p 8501:8501 --name mdo \
  --env-file .env \
  market-data-orchestrator:0.8.0

# View logs
docker logs -f mdo

# Stop container
docker stop mdo && docker rm mdo
```

### Kubernetes

#### Prerequisites

```bash
# Create namespace
kubectl create namespace market-data

# Create secrets (Phase 6.3)
kubectl create secret generic mdo-secrets \
  --from-literal=api-key=your-secret-key \
  --from-literal=oidc-issuer=https://tenant.auth0.com/ \
  --from-literal=oidc-audience=market-data-orchestrator \
  --from-literal=jwks-url=https://tenant.auth0.com/.well-known/jwks.json \
  -n market-data
```

#### Deploy

```bash
# Apply all manifests
kubectl apply -f deploy/k8s/

# Check deployment status
kubectl get pods -n market-data -l app=mdo-orchestrator

# View logs
kubectl logs -n market-data -l app=mdo-orchestrator -f

# Port forward for local access
kubectl port-forward -n market-data svc/mdo-orchestrator 8080:80
```

#### Verify Deployment

```bash
# Test health endpoint
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://mdo-orchestrator.market-data/health

# Expected response:
{"service": "orchestrator", "state": "healthy", ...}

# Test topology endpoint (Phase 8.0)
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://mdo-orchestrator.market-data/federation/topology
```

#### Scale & Update

```bash
# Scale deployment (if needed)
kubectl scale deployment mdo-orchestrator -n market-data --replicas=2

# Update image
kubectl set image deployment/mdo-orchestrator \
  orchestrator=market-data-orchestrator:0.6.0 \
  -n market-data

# Check rollout status
kubectl rollout status deployment/mdo-orchestrator -n market-data

# Rollback if needed
kubectl rollout undo deployment/mdo-orchestrator -n market-data
```

---

## 📊 Monitoring & Observability

### Prometheus Metrics

Access metrics at: `http://localhost:8501/metrics`

#### Core Metrics

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `orchestrator_status` | Gauge | - | Running state (1=running, 0=stopped) |
| `pipeline_events_total` | Counter | - | Total events processed by pipeline |
| `feedback_events_total` | Counter | `event_type` | Feedback events received from store |
| `provider_connection_status` | Gauge | - | Provider connection state (1=connected, 0=disconnected) |

#### Control Plane Metrics (Phase 6.2/6.3)

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `orchestrator_control_actions_total` | Counter | `action`, `status` | Control actions (pause/resume/reload) with success/error |
| `orchestrator_ws_clients` | Gauge | - | Active WebSocket connections |
| `orchestrator_auth_failures_total` | Counter | `reason` | Authentication failures by reason |
| `orchestrator_rate_limit_hits_total` | Counter | `action`, `result` | Rate limit checks (allowed/denied) |
| `orchestrator_audit_events_total` | Counter | `action`, `status` | Audit events logged |
| `orchestrator_federation_requests_total` | Counter | `target`, `action`, `status` | Federation requests to peers |

**Example Queries:**
```promql
# Control action rate (per minute)
rate(orchestrator_control_actions_total[1m])

# Failed control actions
orchestrator_control_actions_total{status="error"}

# WebSocket connection count
orchestrator_ws_clients

# Auth failure rate
rate(orchestrator_auth_failures_total[5m])

# Rate limit hit ratio
rate(orchestrator_rate_limit_hits_total{result="denied"}[1m]) 
  / rate(orchestrator_rate_limit_hits_total[1m])
```

### Grafana Integration

1. **Add Prometheus datasource** in Grafana
2. **Import dashboard** templates:
   - Orchestrator Overview
   - Control Plane Analytics
   - Federation Topology
3. **Configure alerts**:
   - Orchestrator down for > 1 minute
   - Provider disconnected for > 30 seconds
   - High backpressure events (> 10/min)
   - Control action failures
   - Auth failure spike
   - Rate limit threshold exceeded

### Logging

Structured logs support both JSON and text formats.

**JSON Format (production):**
```json
{
  "timestamp": "2025-10-17T14:30:00Z",
  "level": "INFO",
  "logger": "market_data_orchestrator.orchestrator",
  "message": "Orchestrator started",
  "extra": {"running": true, "mode": "dag", "version": "0.6.0"}
}
```

**Text Format (development):**
```
2025-10-17 14:30:00 [INFO] market_data_orchestrator.orchestrator: Orchestrator started
```

### Audit Logging (Phase 6.3)

Persistent JSONL audit trail for all control actions:

```jsonl
{"ts": 1729197600.0, "actor": "operator@example.com", "role": "operator", "action": "pause", "result": {"status": "ok", "detail": "Orchestrator paused"}}
{"ts": 1729197630.0, "actor": "admin@example.com", "role": "admin", "action": "reload", "result": {"status": "ok", "detail": "Config reloaded"}}
```

**Query recent audit events:**
```python
from market_data_orchestrator.audit.logger import get_audit_logger

audit_logger = get_audit_logger()
recent_events = audit_logger.get_recent_events(limit=100)
```

---

## 🔧 Development

### Setup Development Environment

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run code formatters
black src/ tests/

# Run linter
ruff check src/ tests/

# Type checking (optional)
mypy src/
```

### Project Structure

```
market_data_orchestrator/
├── src/
│   └── market_data_orchestrator/
│       ├── __init__.py              # Package initialization
│       ├── launcher.py              # Entry point (async main)
│       ├── health.py                # FastAPI app factory + ServiceContainer
│       ├── logging_config.py        # Structured logging setup
│       ├── settings.py              # Settings facade (Phase 3)
│       ├── feedback.py              # Feedback bus subscribers
│       ├── config/                  # Phase 3: Focused settings groups
│       │   ├── runtime.py           # RuntimeSettings (ISP)
│       │   ├── feedback.py          # FeedbackSettings (ISP)
│       │   ├── security.py          # SecuritySettings (ISP)
│       │   ├── provider.py          # ProviderSettings (ISP)
│       │   ├── infrastructure.py    # InfrastructureSettings (ISP)
│       │   └── unified.py           # OrchestratorSettings (facade)
│       ├── _internal/               # Phase 1-2: Internal refactored components
│       │   ├── container.py         # ServiceContainer (DI)
│       │   ├── lifecycle.py         # LifecycleManager (SRP)
│       │   ├── control_plane.py     # ControlPlaneService (SRP)
│       │   ├── status_aggregator.py # StatusAggregator (SRP)
│       │   ├── orchestrator.py      # Refactored MarketDataOrchestrator
│       │   ├── rate_limiter.py      # RedisRateLimiter (Phase 1)
│       │   └── event_registry.py    # EventRegistry + handlers (Phase 3, OCP)
│       ├── protocols/               # Phase 1: Protocol definitions
│       │   ├── provider.py          # Provider protocol
│       │   ├── runtime.py           # Runtime protocol
│       │   ├── feedback.py          # FeedbackBus protocol
│       │   ├── rate_limiter.py      # RateLimiter protocol
│       │   └── audit.py             # AuditLogger protocol
│       ├── services/                # Phase 8.0: Services
│       │   └── federation_directory.py # StaticDirectory (FederationDirectory)
│       ├── api/                     # API routers
│       │   ├── deps.py              # Dependency injection (Phase 1)
│       │   ├── auth.py              # API key authentication
│       │   ├── auth_jwt.py          # JWT/OIDC authentication (Phase 6.3)
│       │   ├── control.py           # Control plane endpoints
│       │   ├── rate_limit.py        # Rate limiting (Phase 6.3)
│       │   ├── federation.py        # Federation endpoints (Phase 6.3 + 8.0)
│       │   └── websocket.py         # WebSocket broadcaster
│       ├── audit/                   # Phase 6.3: Audit logging
│       │   └── logger.py            # Persistent JSONL audit logger
│       ├── models/                  # Data models
│       │   └── security.py          # RBAC roles (Phase 6.3)
│       └── ui/                      # Cockpit dashboard
│           └── static/
│               ├── index.html       # Dashboard UI
│               └── cockpit.js       # Dashboard logic
├── tests/
│   ├── conftest.py                  # Pytest fixtures (Phase 1 updated)
│   ├── unit/                        # Unit tests
│   │   ├── test_settings.py         # Settings validation
│   │   ├── test_feedback.py         # Feedback subscribers
│   │   ├── test_orchestrator_lifecycle.py # Lifecycle tests
│   │   └── test_health_endpoints.py # Health API tests
│   ├── integration/                 # Integration tests
│   │   ├── test_e2e_launch.py       # E2E orchestrator startup
│   │   └── test_feedback_flow.py    # Feedback bus integration
│   ├── api/                         # Phase 8.0: Contract tests
│   │   ├── test_health_contract.py  # HealthStatus schema tests
│   │   ├── test_control_audit_contract.py # ControlResult/AuditEnvelope tests
│   │   ├── test_federation_contract.py # ClusterTopology tests
│   │   └── test_schemas.py          # Schema snapshot tests
│   ├── services/                    # Phase 8.0: Service tests
│   │   └── test_federation_directory.py # StaticDirectory tests
│   ├── test_auth.py                 # API key auth tests
│   ├── test_auth_jwt.py             # JWT/OIDC tests (Phase 6.3)
│   ├── test_control.py              # Control API tests
│   ├── test_rate_limit.py           # Rate limiting tests (Phase 6.3)
│   ├── test_federation.py           # Federation tests (Phase 6.3)
│   ├── test_audit.py                # Audit logging tests (Phase 6.3)
│   └── test_websocket.py            # WebSocket tests
├── deploy/
│   ├── Dockerfile                   # Docker image definition
│   └── k8s/                         # Kubernetes manifests
│       ├── deployment.yaml          # K8s Deployment
│       ├── service.yaml             # K8s Service
│       └── orchestrator-secrets.yaml # K8s Secrets (Phase 6.3)
├── docs/                            # Documentation
│   ├── ARCHITECTURE_OVERVIEW.md     # Architecture deep dive
│   ├── PHASE_6.1_*.md               # Phase 6.1 docs
│   ├── PHASE_6.2_*.md               # Phase 6.2 docs
│   └── PHASE_6.3_*.md               # Phase 6.3 docs
├── .cursor/                         # Cursor IDE rules
├── CHANGELOG.md                     # Version history
├── pyproject.toml                   # Project metadata & dependencies
├── requirements.txt                 # Production dependencies
├── requirements-dev.txt             # Development dependencies
└── README.md                        # This file
```

### Code Style

- **Line length**: 100 characters
- **Type hints**: Required for all public functions
- **Imports**: Use `from __future__ import annotations`
- **Async**: Use `async def` for I/O-bound operations
- **Logging**: Use structured logging (no `print()`)
- **SOLID**: Follow SOLID principles (see Phase 3 docs)

### Commit Message Format

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test updates
- `refactor`: Code refactoring
- `chore`: Maintenance tasks
- `contract`: Phase 8.0 contract adoption

**Examples:**
```
feat: add WebSocket status broadcaster

fix: handle Redis connection failures in rate limiter

docs: update API documentation with Phase 8.0 contracts

test: add contract tests for Core HealthStatus schema

refactor: extract control plane service (Phase 2 SRP)

contract: adopt Core v1.1.0 telemetry contracts
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Import Errors on Startup

**Symptom:**
```
ModuleNotFoundError: No module named 'market_data_core'
```

**Solution:**
```bash
# Install market data stack
pip install market-data-core==1.1.0
pip install market-data-pipeline==0.8.1
pip install market-data-store==0.3.0
pip install market-data-ibkr==1.0.0

# Or reinstall package
pip install -e .
```

#### 2. Health Endpoint Returns Degraded/Unhealthy

**Symptom:**
```bash
curl http://localhost:8501/health
# Returns: {"service": "orchestrator", "state": "unhealthy", "components": [...]}
```

**Possible Causes:**
- Dependencies not available (provider, feedback bus)
- Provider connection failed
- Redis unavailable

**Solution:**
```bash
# Check logs for specific errors
python -m market_data_orchestrator.launcher

# Try disabling feedback bus temporarily
export ORCH_FEEDBACK_ENABLED=false
python -m market_data_orchestrator.launcher

# Verify Redis is running
redis-cli ping
```

#### 3. WebSocket Connection Fails

**Symptom:** Dashboard shows "WebSocket: disconnected"

**Solutions:**
- Verify server is running: `curl http://localhost:8501/health`
- Check browser console for errors (F12 → Console)
- Ensure firewall allows WebSocket connections
- Verify correct base URL in dashboard config

#### 4. Control Endpoints Return 401 Unauthorized

**Symptom:**
```bash
curl -X POST http://localhost:8501/control/pause
# Returns: 401 Unauthorized
```

**Solution:**
```bash
# Set API key
export ORCH_API_KEY="your-secret-key"

# Restart server and include auth header
curl -X POST -H "X-API-Key: your-secret-key" \
  http://localhost:8501/control/pause

# Or use JWT token
curl -X POST -H "Authorization: Bearer eyJhbGc..." \
  http://localhost:8501/control/pause
```

#### 5. JWT Authentication Fails (Phase 6.3)

**Symptom:**
```
{"detail": "Could not validate credentials"}
```

**Solutions:**
- Verify OIDC issuer and audience match token claims
- Check JWKS URL is accessible
- Ensure token is not expired
- Verify role claim is present in token

```bash
# Debug JWT token (jwt.io)
echo $JWT_TOKEN | base64 -d

# Test JWKS endpoint
curl https://YOUR_TENANT.auth0.com/.well-known/jwks.json
```

#### 6. Rate Limit Exceeded (HTTP 429)

**Symptom:**
```
{"detail": "Rate limit exceeded: max 5/pause/min"}
```

**Solution:**
- Wait 1 minute before retrying
- Control endpoints limited to 5 actions/minute per action type
- Check Redis connection if rate limit not working

#### 7. Federation Topology Returns Empty Nodes (Phase 8.0)

**Symptom:**
```json
{"cluster_id": {"value": "default"}, "region": {"name": "local"}, "nodes": []}
```

**Solution:**
```bash
# Check federation peers configuration
echo $ORCH_FEDERATION_PEERS

# Should be comma-separated URLs
export ORCH_FEDERATION_PEERS="http://mdp-us:8080,http://mds-eu:8080"
```

### Debug Mode

```bash
# Enable debug logging
export ORCH_LOG_LEVEL=DEBUG

# Use text format for easier reading
export ORCH_LOG_FORMAT=text

# Start server
python -m market_data_orchestrator.launcher

# Check verbose output
```

### Getting Help

- **Documentation**: See `docs/` directory for detailed guides
- **Issues**: [GitHub Issues](https://github.com/mjdevaccount/market_data_orchestrator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mjdevaccount/market_data_orchestrator/discussions)
- **CHANGELOG**: See [CHANGELOG.md](CHANGELOG.md) for version history

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/market_data_orchestrator.git
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```

### Development Workflow

1. **Install dev dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

2. **Make your changes**
   - Follow existing code style and patterns
   - Maintain SOLID principles (see Phase 3 docs)
   - Add tests for new functionality
   - Update documentation as needed
   - Add contract tests for Core schema changes (Phase 8.0)

3. **Run tests**:
   ```bash
   pytest -v
   ```

4. **Format code**:
   ```bash
   black src/ tests/
   ruff check src/ tests/
   ```

5. **Commit changes**:
   ```bash
   git commit -m "feat: add amazing feature"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**

### Contribution Guidelines

- **Tests Required**: All new features must include tests
- **Documentation**: Update README.md and relevant docs
- **Code Style**: Follow existing patterns (100 char line length, type hints, etc.)
- **SOLID Principles**: Maintain architectural integrity
- **Commit Messages**: Use conventional commits format
- **One Feature per PR**: Keep pull requests focused
- **Contract Compliance**: Ensure Core schema compatibility (Phase 8.0+)

### Code Review Process

1. Automated checks run (tests, linting, type checking)
2. Maintainer reviews code and provides feedback
3. Address feedback and push updates
4. Once approved, maintainer merges PR

### Architecture Guidelines (SOLID)

When contributing, please maintain SOLID principles:

- **SRP**: Keep services focused on one responsibility
- **OCP**: Extend via protocols, not modification
- **LSP**: Protocol implementations must be substitutable
- **ISP**: Use focused settings groups, avoid god objects
- **DIP**: Depend on protocols, not concrete implementations

See [`docs/ARCHITECTURE_OVERVIEW.md`](docs/ARCHITECTURE_OVERVIEW.md) for details.

---

## 📚 Documentation

### Core Documentation
- **[Architecture Overview](docs/ARCHITECTURE_OVERVIEW.md)** - Deep dive into system design
- **[CHANGELOG](CHANGELOG.md)** - Version history and release notes

### Phase Documentation
- **[Phase 6.1 Implementation Plan](docs/PHASE_6.1_IMPLEMENTATION_PLAN.md)** - Core orchestration development
- **[Phase 6.1 Verification Guide](docs/PHASE_6.1_VERIFICATION_GUIDE.md)** - Testing and validation
- **[Phase 6.2 Implementation Plan](docs/PHASE_6.2_IMPLEMENTATION_PLAN.md)** - Cockpit & control plane
- **[Phase 6.2 Verification Guide](docs/PHASE_6.2_VERIFICATION_GUIDE.md)** - Cockpit testing
- **[Phase 6.3 OIDC Setup](docs/PHASE_6.3_OIDC_SETUP.md)** - JWT/OIDC authentication guide

### Contract Documentation (Phase 8.0)
- **[Core v1.1.0 Release](https://github.com/mjdevaccount/market-data-core/releases/tag/v1.1.0)** - Core contracts reference
- Contract tests in `tests/api/test_*_contract.py`
- Schema snapshot tests in `tests/api/test_schemas.py`

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 mjdevaccount

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [Uvicorn](https://www.uvicorn.org/) - Lightning-fast ASGI server
- [Pydantic](https://docs.pydantic.dev/) - Data validation and settings
- [Prometheus Client](https://github.com/prometheus/client_python) - Metrics export
- [Redis](https://redis.io/) - In-memory data structure store
- [python-jose](https://python-jose.readthedocs.io/) - JWT implementation

### Related Projects
- [market-data-core](https://github.com/mjdevaccount/market-data-core) - Shared contracts and types (v1.1.0)
- [market-data-pipeline](https://github.com/mjdevaccount/market-data-pipeline) - Data processing engine
- [market-data-store](https://github.com/mjdevaccount/market-data-store) - Storage and feedback bus
- [market-data-ibkr](https://github.com/mjdevaccount/market-data-ibkr) - Interactive Brokers provider

---

<div align="center">

**[⬆ Back to Top](#-market-data-orchestrator)**

Made with ❤️ by [Matt Jeffcoat](https://github.com/mjdevaccount)

**Status:** ✅ v0.6.0 Complete (Phase 8.0) | **License:** MIT | **SOLID:** ✓

</div>
