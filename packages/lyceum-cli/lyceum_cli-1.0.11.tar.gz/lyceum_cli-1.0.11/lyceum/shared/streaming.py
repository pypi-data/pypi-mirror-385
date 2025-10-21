"""
Streaming utilities for execution output
"""

import json
import re
import httpx
from rich.console import Console

from .config import config

console = Console()


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from text"""
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return ansi_escape.sub('', text)


def stream_execution_output(execution_id: str, streaming_url: str = None) -> bool:
    """Stream execution output in real-time. Returns True if successful, False if failed."""
    if not streaming_url:
        # Fallback to old endpoint if no streaming URL provided
        stream_url = f"{config.base_url}/api/v2/external/execution/streaming/{execution_id}"
    else:
        stream_url = streaming_url

    try:
        console.print(f"[dim]🔗 Connecting to execution stream...[/dim]")
        console.print(f"[dim]Stream URL: {stream_url}[/dim]")

        with httpx.stream("GET", stream_url, headers={"Authorization": f"Bearer {config.api_key}"}, timeout=600.0) as response:
            if response.status_code != 200:
                console.print(f"[red]❌ Stream failed: HTTP {response.status_code}[/red]")
                return False
            
            console.print("[dim]📡 Streaming output...[/dim]")
            
            for line in response.iter_lines():
                if line.strip():
                    # Parse Server-Sent Events format
                    if line.startswith("data: "):
                        data_json = line[6:]  # Remove "data: " prefix
                        try:
                            data = json.loads(data_json)
                            event_type = data.get("type", "unknown")
                            
                            if event_type == "output":
                                # Print output without extra formatting, stripping ANSI codes
                                output = data.get("content", "")  # Fixed: server sends "content" not "output"
                                if output:
                                    clean_output = strip_ansi_codes(output)
                                    console.print(clean_output, end="")
                            
                            elif event_type == "completed":
                                status = data.get("status", "unknown")
                                exec_time = data.get("execution_time", 0)
                                
                                if status == "completed":
                                    console.print(f"\n[green]✅ Execution completed successfully in {exec_time:.1f}s[/green]")
                                elif status in ["failed_user", "failed_system"]:
                                    console.print(f"\n[red]❌ Execution failed: {status}[/red]")
                                    # Show errors if available
                                    errors = data.get("errors")
                                    if errors:
                                        console.print(f"[red]Error: {errors}[/red]")
                                elif status == "timeout":
                                    console.print(f"\n[yellow]⏰ Execution timed out after {exec_time:.1f}s[/yellow]")
                                elif status == "cancelled":
                                    console.print(f"\n[yellow]🛑 Execution was cancelled[/yellow]")
                                
                                return status == "completed"
                            
                            elif event_type == "error":
                                error_msg = data.get("message", "Unknown error")
                                console.print(f"\n[red]❌ Error: {error_msg}[/red]")
                                return False
                                
                        except json.JSONDecodeError:
                            # Skip malformed JSON
                            continue
            
            console.print(f"\n[yellow]⚠️ Stream ended without completion signal[/yellow]")
            # Fallback: poll execution status
            return check_execution_status(execution_id)

    except Exception as e:
        console.print(f"\n[red]❌ Streaming error: {e}[/red]")
        # Fallback: poll execution status
        return check_execution_status(execution_id)


def check_execution_status(execution_id: str) -> bool:
    """Check execution status as fallback when streaming fails."""
    import time

    console.print("[dim]⏳ Checking execution status...[/dim]")

    for _ in range(30):  # Poll for up to 30 seconds
        try:
            response = httpx.get(
                f"{config.base_url}/api/v2/external/execution/streaming/{execution_id}/status",
                headers={"Authorization": f"Bearer {config.api_key}"},
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')

                if status == 'completed':
                    console.print(f"[green]✅ Execution completed successfully![/green]")
                    return True
                elif status in ['failed_user', 'failed_system', 'failed']:
                    console.print(f"[red]❌ Execution failed: {status}[/red]")
                    errors = data.get('errors')
                    if errors:
                        console.print(f"[red]Error: {errors}[/red]")
                    return False
                elif status in ['timeout', 'cancelled']:
                    console.print(f"[yellow]⚠️ Execution {status}[/yellow]")
                    return False
                elif status in ['running', 'pending', 'queued']:
                    # Still running, continue polling
                    time.sleep(1)
                    continue

        except Exception as e:
            console.print(f"[red]Error checking status: {e}[/red]")
            break

    console.print("[yellow]⚠️ Status check timed out[/yellow]")
    return False