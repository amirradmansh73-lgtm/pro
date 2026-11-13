from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from netbeacon.config import load_config
from netbeacon.monitor import MonitorEngine
from netbeacon.models import TargetConfig

config = load_config()
engine = MonitorEngine(config)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background monitoring loop
    monitor_task = asyncio.create_task(engine.start())
    yield
    engine.stop()
    monitor_task.cancel()
    try:
        await monitor_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="NetBeacon API",
    description="Microservice health monitoring & status API",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/api/status")
async def get_status():
    return {
        "count": len(engine.states),
        "targets": engine.get_states()
    }


@app.post("/api/check-all")
async def check_all():
    await engine.run_cycle()
    return {"message": "Health check cycle completed", "targets": engine.get_states()}


@app.post("/api/targets")
async def add_target(target: TargetConfig):
    if target.name in engine.states:
        raise HTTPException(status_code=400, detail="Target name already exists")
    engine.add_target(target)
    await engine.check_single_target(target.name)
    return {"message": f"Target '{target.name}' added successfully"}


@app.delete("/api/targets/{target_name}")
async def delete_target(target_name: str):
    removed = engine.remove_target(target_name)
    if not removed:
        raise HTTPException(status_code=404, detail="Target not found")
    return {"message": f"Target '{target_name}' deleted"}


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NetBeacon | Status Dashboard</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      min-height: 100vh;
      padding: 2rem 1rem;
    }
    .container { max-width: 1000px; margin: 0 auto; }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 2rem;
      border-bottom: 1px solid #1e293b;
      margin-bottom: 2rem;
    }
    h1 { font-size: 1.75rem; font-weight: 700; color: #38bdf8; }
    .subtitle { font-size: 0.875rem; color: #94a3b8; margin-top: 0.25rem; }
    .btn {
      background: #2563eb;
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 6px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
    }
    .btn:hover { background: #1d4ed8; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem; }
    .card {
      background: #1e293b;
      border: 1px solid #334155;
      border-radius: 10px;
      padding: 1.25rem;
      transition: transform 0.2s, border-color 0.2s;
    }
    .card:hover { transform: translateY(-2px); border-color: #475569; }
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }
    .target-name { font-weight: 600; font-size: 1.1rem; }
    .badge {
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      padding: 0.25rem 0.6rem;
      border-radius: 9999px;
    }
    .badge-up { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
    .badge-down { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-unknown { background: rgba(148, 163, 184, 0.2); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.3); }
    .metric {
      display: flex;
      justify-content: space-between;
      padding: 0.35rem 0;
      font-size: 0.875rem;
      color: #94a3b8;
    }
    .metric-value { color: #f1f5f9; font-weight: 500; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div>
        <h1>NetBeacon</h1>
        <p class="subtitle">Cloud-native service health and latency dashboard</p>
      </div>
      <button class="btn" onclick="refreshData()">Check Now</button>
    </header>

    <div id="targetsGrid" class="grid">
      <div style="color: #64748b;">Loading status...</div>
    </div>
  </div>

  <script>
    async function refreshData() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        renderTargets(data.targets);
      } catch (err) {
        console.error('Error fetching targets:', err);
      }
    }

    function renderTargets(targets) {
      const container = document.getElementById('targetsGrid');
      if (!targets || targets.length === 0) {
        container.innerHTML = '<div style="color: #64748b;">No targets registered.</div>';
        return;
      }

      container.innerHTML = targets.map(t => {
        const badgeClass = t.current_status === 'up' ? 'badge-up' : (t.current_status === 'down' ? 'badge-down' : 'badge-unknown');
        return `
          <div class="card">
            <div class="card-header">
              <span class="target-name">${t.config.name}</span>
              <span class="badge ${badgeClass}">${t.current_status}</span>
            </div>
            <div class="metric">
              <span>Type</span>
              <span class="metric-value">${t.config.type.toUpperCase()}</span>
            </div>
            <div class="metric">
              <span>Uptime SLA</span>
              <span class="metric-value">${t.uptime_percentage}%</span>
            </div>
            <div class="metric">
              <span>Latency</span>
              <span class="metric-value">${t.last_response_time_ms} ms</span>
            </div>
            <div class="metric">
              <span>Total Checks</span>
              <span class="metric-value">${t.total_checks}</span>
            </div>
          </div>
        `;
      }).join('');
    }

    refreshData();
    setInterval(refreshData, 15000);
  </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)
