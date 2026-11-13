import argparse
import asyncio
import sys
import uvicorn
from rich.console import Console
from rich.table import Table
from netbeacon.config import load_config
from netbeacon.monitor import MonitorEngine
from netbeacon.checker import run_target_check
from netbeacon.models import TargetConfig, TargetType

console = Console()


async def run_check_cli(config_path: str):
    config = load_config(config_path)
    engine = MonitorEngine(config)
    
    console.print(f"[bold cyan]NetBeacon[/bold cyan] checking {len(config.targets)} targets...\n")
    await engine.run_cycle()
    
    table = Table(title="Target Status Summary")
    table.add_column("Target", style="bold")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Latency")
    table.add_column("Checks")
    
    for state in engine.get_states():
        status_color = "green" if state.current_status == "up" else "red"
        table.add_row(
            state.config.name,
            state.config.type.value.upper(),
            f"[{status_color}]{state.current_status.value.upper()}[/{status_color}]",
            f"{state.last_response_time_ms} ms",
            f"{state.successful_checks}/{state.total_checks}"
        )
    
    console.print(table)


def start_server_cli(config_path: str):
    config = load_config(config_path)
    console.print(f"[bold green]Starting NetBeacon Server[/bold green] on {config.server.host}:{config.server.port}...")
    uvicorn.run("netbeacon.app:app", host=config.server.host, port=config.server.port, reload=False)


def main():
    parser = argparse.ArgumentParser(description="NetBeacon Service Health Monitor")
    parser.add_argument("-c", "--config", default="netbeacon.yaml", help="Path to config file")
    
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("check", help="Run a single health check cycle in terminal")
    subparsers.add_parser("serve", help="Run the API and web dashboard")
    
    args = parser.parse_args()
    if args.command == "check":
        asyncio.run(run_check_cli(args.config))
    elif args.command == "serve":
        start_server_cli(args.config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
