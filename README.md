# NetBeacon

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

NetBeacon is a lightweight, asynchronous microservice health monitoring and uptime dashboard engine written in Python. It periodically checks the availability, latency, and status of HTTP endpoints and TCP ports, calculates uptime SLAs, alerts via webhooks, and serves an interactive web dashboard.

---

## Key Features

- **Asynchronous Health Checks**: Concurrent, non-blocking polling for HTTP/HTTPS endpoints and TCP services using `asyncio` and `httpx`.
- **Latency & SLA Calculation**: Real-time response time tracking and rolling uptime percentage calculation.
- **Web Dashboard**: Embedded dark-mode UI with live status cards and instant trigger checks.
- **RESTful API**: Programmatic endpoints to inspect status, trigger immediate checks, or register new targets dynamically.
- **Alert Dispatcher**: Webhook integration for instant notifications when service states change (e.g. up to down).
- **CLI Utilities**: Check targets directly in the console with formatted tables using `rich`.
- **Docker Ready**: Pre-configured `Dockerfile` and `docker-compose.yml` for single-command deployment.

---

## Quick Start

### 1. Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/amirradmansh73-lgtm/pro.git
cd pro
pip install -r requirements.txt
pip install -e .
```

### 2. Configuration

Create or edit `netbeacon.yaml`:

```yaml
server:
  host: "0.0.0.0"
  port: 8080

settings:
  check_interval_seconds: 30
  timeout_seconds: 5.0

targets:
  - name: "Google DNS"
    type: "tcp"
    host: "8.8.8.8"
    port: 53

  - name: "Cloudflare"
    type: "http"
    url: "https://1.1.1.1"
    expected_status: 200

alerts:
  webhook_url: "https://your-webhook-endpoint.com/alert"
```

### 3. Running via CLI

Run a single check across all configured targets in the terminal:

```bash
netbeacon check
```

Start the background monitoring engine and web dashboard:

```bash
netbeacon serve
```

Then visit **http://localhost:8080** in your browser.

---

## Docker Deployment

To launch NetBeacon with Docker Compose:

```bash
docker-compose up -d
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web Status Dashboard |
| `GET` | `/api/status` | Current health status and metrics of all targets |
| `POST` | `/api/check-all` | Trigger an immediate manual health check cycle |
| `POST` | `/api/targets` | Register a new monitoring target dynamically |
| `DELETE` | `/api/targets/{name}` | Deregister a monitoring target |
| `GET` | `/docs` | Interactive Swagger API documentation |

---

## Running Tests

NetBeacon includes automated unit tests:

```bash
pytest
```

---

## License

This project is licensed under the [MIT License](LICENSE).
