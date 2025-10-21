import json
import os
import subprocess
import sys
from pathlib import Path

import typer
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
app = typer.Typer(help="HFStudio - Local and API-based Text-to-Speech Studio")


def get_project_root() -> Path:
    """Find the project root directory containing models/"""
    current_dir = Path(__file__).parent
    while current_dir != current_dir.parent:
        if (current_dir / "models").exists():
            return current_dir
        current_dir = current_dir.parent

    # Fallback to current working directory
    if (Path.cwd() / "models").exists():
        return Path.cwd()

    raise FileNotFoundError("Could not find models/ directory")


def load_model_specs():
    """Load model specifications from models/ directory"""
    project_root = get_project_root()
    models_dir = project_root / "models"

    model_registry = {}

    # Scan for model directories with spec.json files
    for model_dir in models_dir.iterdir():
        if model_dir.is_dir():
            spec_file = model_dir / "spec.json"
            local_script = model_dir / "local.py"

            if spec_file.exists():
                try:
                    with open(spec_file, "r") as f:
                        spec = json.load(f)

                    model_name = model_dir.name
                    model_registry[model_name] = {
                        "script": str(local_script) if local_script.exists() else None,
                        "spec": spec,
                        "description": spec.get("description", ""),
                        "status": "Available" if local_script.exists() else "Spec Only",
                    }

                    # Also register by full model_id if different
                    if spec.get("model_id") and spec["model_id"] != model_name:
                        model_registry[spec["model_id"]] = model_registry[model_name]

                except json.JSONDecodeError:
                    console.print(
                        f"[yellow]Warning: Invalid JSON in {spec_file}[/yellow]"
                    )

    return model_registry


# Load models dynamically
MODEL_REGISTRY = load_model_specs()


def run_model_script(model_name: str, port: int, host: str):
    """Run a model's UV script"""
    if model_name not in MODEL_REGISTRY:
        available_models = ", ".join(MODEL_REGISTRY.keys())
        console.print(f"[red]Error: Unknown model '{model_name}'[/red]")
        console.print(f"[yellow]Available models: {available_models}[/yellow]")
        return False

    model_info = MODEL_REGISTRY[model_name]
    script_path = model_info["script"]

    if not script_path:
        console.print(f"[red]Error: Model '{model_name}' is not yet implemented[/red]")
        return False

    project_root = get_project_root()
    full_script_path = project_root / script_path

    if not full_script_path.exists():
        console.print(f"[red]Error: Model script not found: {full_script_path}[/red]")
        return False

    console.print(f"[green]Starting {model_name} on {host}:{port}[/green]")
    console.print(f"[dim]Script: {full_script_path}[/dim]")

    # Run the UV script
    cmd = [
        "uv",
        "run",
        str(full_script_path),
        "--port",
        str(port),
        "--host",
        host,
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running model: {e}[/red]")
        return False
    except KeyboardInterrupt:
        console.print("\n[yellow]Model server stopped[/yellow]")
        return True

    return True


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Welcome to HFStudio CLI"""
    if ctx.invoked_subcommand is None:
        console.print(
            Panel.fit(
                "[bold yellow]🎙️ HFStudio CLI[/bold yellow]\n\n"
                "[green]Available Commands:[/green]\n"
                "• [cyan]hfstudio start[/cyan] <model>    - Start a TTS model locally\n"
                "• [cyan]hfstudio list[/cyan]             - List available models\n"
                "• [cyan]hfstudio --help[/cyan]           - Show detailed help\n\n"
                "[dim]Example: hfstudio start resambleai/chatterbox --port 1234[/dim]",
                title="🎙️ HFStudio",
                border_style="yellow",
            )
        )


@app.command()
def start(
    model: str = typer.Argument(..., help="Model name (e.g., resambleai/chatterbox)"),
    port: int = typer.Option(7860, "--port", "-p", help="Port to run the model on"),
    host: str = typer.Option("0.0.0.0", "--host", help="Host to run the model on"),
):
    """Start a TTS model locally"""
    success = run_model_script(model, port, host)
    if not success:
        raise typer.Exit(1)


@app.command()
def list():
    """List available TTS models"""
    table = Table(title="Available TTS Models")
    table.add_column("Model", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Status", style="yellow")

    for model_name, model_info in MODEL_REGISTRY.items():
        table.add_row(model_name, model_info["description"], model_info["status"])

    console.print(table)


@app.command()
def dev_server(
    port: int = typer.Option(7860, "--port", "-p", help="Port to run the server on"),
    host: str = typer.Option("0.0.0.0", "--host", help="Host to run the server on"),
    dev: bool = typer.Option(False, "--dev", help="Run in development mode"),
):
    """Start the HFStudio development server"""

    console.print(
        Panel.fit(
            "[bold green]HFStudio Development Server[/bold green]\n"
            f"Running on http://{host if host != '0.0.0.0' else 'localhost'}:{port}\n"
            f"API docs: http://localhost:{port}/docs",
            title="🎙️ HFStudio Dev Server",
            border_style="green",
        )
    )

    uvicorn.run(
        "hfstudio.server:app",
        host=host,
        port=port,
        reload=dev,
        log_level="info" if not dev else "debug",
    )


if __name__ == "__main__":
    app()
