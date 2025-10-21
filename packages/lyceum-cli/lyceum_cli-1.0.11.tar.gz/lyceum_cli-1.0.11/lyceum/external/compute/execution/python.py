"""
Python execution commands
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
import httpx

from ....shared.config import config
from ....shared.streaming import stream_execution_output

console = Console()

python_app = typer.Typer(name="python", help="Python execution commands")


@python_app.command("run")
def run_python(
    code_or_file: str = typer.Argument(..., help="Python code to execute or path to Python file"),
    machine_type: str = typer.Option("cpu", "--machine", "-m", help="Machine type (cpu, a100, h100, etc.)"),
    timeout: int = typer.Option(60, "--timeout", "-t", help="Execution timeout in seconds"),
    file_name: Optional[str] = typer.Option(None, "--file-name", "-f", help="Name for the execution"),
    requirements: Optional[str] = typer.Option(None, "--requirements", "-r", help="Requirements file path or pip requirements string"),
    imports: Optional[list[str]] = typer.Option(None, "--import", help="Pre-import modules (can be used multiple times)"),
):
    """Execute Python code or file on Lyceum Cloud"""
    try:
        # Check if it's a file path
        code_to_execute = code_or_file
        if Path(code_or_file).exists():
            console.print(f"[dim]Reading code from file: {code_or_file}[/dim]")
            with open(code_or_file, 'r') as f:
                code_to_execute = f.read()
            # Use filename as execution name if not provided
            if not file_name:
                file_name = Path(code_or_file).name

        # Handle requirements
        requirements_content = None
        if requirements:
            # Check if it's a file path
            if Path(requirements).exists():
                console.print(f"[dim]Reading requirements from file: {requirements}[/dim]")
                with open(requirements, 'r') as f:
                    requirements_content = f.read()
            else:
                # Treat as direct pip requirements string
                requirements_content = requirements

        # Create execution request payload
        payload = {
            "code": code_to_execute,
            "nbcode": 0,
            "execution_type": machine_type,
            "timeout": timeout,
        }

        if file_name:
            payload["file_name"] = file_name
        if requirements_content:
            payload["requirements_content"] = requirements_content
        if imports:
            payload["prior_imports"] = imports

        # Make API request
        response = httpx.post(
            f"{config.base_url}/api/v2/external/execution/streaming/start",
            headers={"Authorization": f"Bearer {config.api_key}"},
            json=payload,
            timeout=30.0
        )

        if response.status_code != 200:
            console.print(f"[red]Error: HTTP {response.status_code}[/red]")
            console.print(f"[red]{response.content.decode()}[/red]")
            raise typer.Exit(1)

        data = response.json()
        execution_id = data['execution_id']
        streaming_url = data.get('streaming_url')

        console.print(f"[green]✅ Execution started![/green]")
        console.print(f"[dim]Execution ID: {execution_id}[/dim]")

        if 'pythia_decision' in data:
            console.print(f"[dim]Pythia recommendation: {data['pythia_decision']}[/dim]")

        # Stream the execution output
        success = stream_execution_output(execution_id, streaming_url)
        
        if not success:
            console.print(f"[yellow]💡 You can check the execution later with: lyceum status[/yellow]")
            raise typer.Exit(1)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)