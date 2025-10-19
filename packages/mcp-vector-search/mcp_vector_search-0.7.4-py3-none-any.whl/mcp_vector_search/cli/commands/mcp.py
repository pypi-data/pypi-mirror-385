"""MCP integration commands for Claude Code."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ...core.exceptions import ProjectNotFoundError
from ...core.project import ProjectManager
from ..didyoumean import create_enhanced_typer
from ..output import print_error, print_info, print_success, print_warning

# Create MCP subcommand app with "did you mean" functionality
mcp_app = create_enhanced_typer(help="Manage Claude Code MCP integration")

console = Console()


def get_claude_command() -> str | None:
    """Get the Claude Code command path."""
    # Check if claude command is available
    claude_cmd = shutil.which("claude")
    if claude_cmd:
        return "claude"

    # Check common installation paths
    possible_paths = [
        "/usr/local/bin/claude",
        "/opt/homebrew/bin/claude",
        os.path.expanduser("~/.local/bin/claude"),
    ]

    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path

    return None


def check_claude_code_available() -> bool:
    """Check if Claude Code is available."""
    claude_cmd = get_claude_command()
    if not claude_cmd:
        return False

    try:
        result = subprocess.run(
            [claude_cmd, "--version"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_mcp_server_command(
    project_root: Path, enable_file_watching: bool = True
) -> str:
    """Get the command to run the MCP server.

    Args:
        project_root: Path to the project root directory
        enable_file_watching: Whether to enable file watching (default: True)
    """
    # Always use the current Python executable for project-scoped installation
    python_exe = sys.executable
    watch_flag = "" if enable_file_watching else " --no-watch"
    return f"{python_exe} -m mcp_vector_search.mcp.server{watch_flag} {project_root}"


def create_project_claude_config(
    project_root: Path, server_name: str, enable_file_watching: bool = True
) -> None:
    """Create or update project-level .mcp.json file.

    Args:
        project_root: Path to the project root directory
        server_name: Name for the MCP server
        enable_file_watching: Whether to enable file watching (default: True)
    """
    # Path to .mcp.json in project root (recommended by Claude Code)
    mcp_config_path = project_root / ".mcp.json"

    # Load existing config or create new one
    if mcp_config_path.exists():
        with open(mcp_config_path) as f:
            config = json.load(f)
    else:
        config = {}

    # Ensure mcpServers section exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    # Use uv for better compatibility, with proper args structure
    config["mcpServers"][server_name] = {
        "type": "stdio",
        "command": "uv",
        "args": ["run", "mcp-vector-search", "mcp"],
        "env": {
            "MCP_ENABLE_FILE_WATCHING": "true" if enable_file_watching else "false"
        },
    }

    # Write the config
    with open(mcp_config_path, "w") as f:
        json.dump(config, f, indent=2)

    print_success("Created project-level .mcp.json with MCP server configuration")
    if enable_file_watching:
        print_info("File watching is enabled for automatic reindexing")
    else:
        print_info("File watching is disabled")


@mcp_app.command("install")
@mcp_app.command("init", hidden=False)  # Add 'init' as an alias
def install_mcp_integration(
    ctx: typer.Context,
    server_name: str = typer.Option(
        "mcp-vector-search",
        "--name",
        help="Name for the MCP server",
        rich_help_panel="📁 Configuration",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force installation even if server already exists",
        rich_help_panel="⚙️  Advanced Options",
    ),
    no_watch: bool = typer.Option(
        False,
        "--no-watch",
        help="Disable file watching for automatic reindexing",
        rich_help_panel="⚙️  Advanced Options",
    ),
) -> None:
    """🔗 Install MCP integration for Claude Code in the current project.

    Creates .mcp.json to enable semantic code search in Claude Code.
    The integration provides AI-powered semantic search tools directly in Claude Code.

    [bold cyan]Basic Examples:[/bold cyan]

    [green]Install with defaults:[/green]
        $ mcp-vector-search mcp install

    [green]Install with custom server name:[/green]
        $ mcp-vector-search mcp install --name my-search-server

    [green]Reinstall/update configuration:[/green]
        $ mcp-vector-search mcp install --force

    [bold cyan]Advanced:[/bold cyan]

    [green]Disable file watching:[/green]
        $ mcp-vector-search mcp install --no-watch

    [dim]💡 Tip: The .mcp.json file can be committed to share
       MCP integration with your team.[/dim]
    """
    try:
        # Get project root for checking initialization
        project_root = ctx.obj.get("project_root") or Path.cwd()

        # Check if project is initialized
        project_manager = ProjectManager(project_root)
        if not project_manager.is_initialized():
            print_error("Project not initialized. Run 'mcp-vector-search init' first.")
            raise typer.Exit(1)

        # Check if .mcp.json already has the server configuration
        mcp_config_path = project_root / ".mcp.json"
        if mcp_config_path.exists() and not force:
            with open(mcp_config_path) as f:
                config = json.load(f)
            if config.get("mcpServers", {}).get(server_name):
                print_warning(f"MCP server '{server_name}' already exists in .mcp.json")
                print_info("Use --force to overwrite")
                raise typer.Exit(1)

        # Create configuration in project root
        enable_file_watching = not no_watch
        create_project_claude_config(project_root, server_name, enable_file_watching)

        print_info(f"MCP server '{server_name}' installed in {mcp_config_path}")
        print_info(
            "Claude Code will automatically detect the server when you open this project"
        )

        # Test the server (using project_root for the server command)
        print_info("Testing server startup...")

        # Get the server command
        server_command = get_mcp_server_command(project_root, enable_file_watching)
        test_process = subprocess.Popen(
            server_command.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Send a simple initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"},
            },
        }

        try:
            test_process.stdin.write(json.dumps(init_request) + "\n")
            test_process.stdin.flush()

            # Wait for response with timeout
            test_process.wait(timeout=5)

            if test_process.returncode == 0:
                print_success("✅ MCP server starts successfully")
            else:
                stderr_output = test_process.stderr.read()
                print_warning(f"⚠️  Server startup test inconclusive: {stderr_output}")

        except subprocess.TimeoutExpired:
            test_process.terminate()
            print_success("✅ MCP server is responsive")

        # Show available tools
        table = Table(title="Available MCP Tools")
        table.add_column("Tool", style="cyan")
        table.add_column("Description", style="white")

        table.add_row("search_code", "Search for code using semantic similarity")
        table.add_row(
            "search_similar", "Find code similar to a specific file or function"
        )
        table.add_row(
            "search_context", "Search for code based on contextual description"
        )
        table.add_row(
            "get_project_status", "Get project indexing status and statistics"
        )
        table.add_row("index_project", "Index or reindex the project codebase")

        if enable_file_watching:
            console.print(
                "\n[green]✅ File watching is enabled[/green] - Changes will be automatically indexed"
            )
        else:
            console.print(
                "\n[yellow]⚠️  File watching is disabled[/yellow] - Manual reindexing required for changes"
            )

        console.print(table)

        print_info("\nTo test the integration, run: mcp-vector-search mcp test")

    except ProjectNotFoundError:
        print_error(f"Project not initialized at {project_root}")
        print_info("Run 'mcp-vector-search init' in the project directory first")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Installation failed: {e}")
        raise typer.Exit(1)


@mcp_app.command("test")
def test_mcp_integration(
    ctx: typer.Context,
    server_name: str = typer.Option(
        "mcp-vector-search",
        "--name",
        help="Name of the MCP server to test",
        rich_help_panel="📁 Configuration",
    ),
) -> None:
    """🧪 Test the MCP integration.

    Verifies that the MCP server is properly configured and can start successfully.
    Use this to diagnose integration issues.

    [bold cyan]Examples:[/bold cyan]

    [green]Test default server:[/green]
        $ mcp-vector-search mcp test

    [green]Test custom server:[/green]
        $ mcp-vector-search mcp test --name my-search-server

    [dim]💡 Tip: Run this after installation to verify everything works.[/dim]
    """
    try:
        # Get project root
        project_root = ctx.obj.get("project_root") or Path.cwd()

        # Check if Claude Code is available
        if not check_claude_code_available():
            print_error("Claude Code not found. Please install Claude Code first.")
            raise typer.Exit(1)

        claude_cmd = get_claude_command()

        # Check if server exists
        print_info(f"Testing MCP server '{server_name}'...")

        try:
            result = subprocess.run(
                [claude_cmd, "mcp", "get", server_name],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                print_error(f"MCP server '{server_name}' not found.")
                print_info(
                    "Run 'mcp-vector-search mcp install' or 'mcp-vector-search mcp init' first"
                )
                raise typer.Exit(1)

            print_success(f"✅ MCP server '{server_name}' is configured")

            # Test if we can run the server directly
            print_info("Testing server startup...")

            server_command = get_mcp_server_command(project_root)
            test_process = subprocess.Popen(
                server_command.split(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Send a simple initialization request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0.0"},
                },
            }

            try:
                test_process.stdin.write(json.dumps(init_request) + "\n")
                test_process.stdin.flush()

                # Wait for response with timeout
                test_process.wait(timeout=5)

                if test_process.returncode == 0:
                    print_success("✅ MCP server starts successfully")
                else:
                    stderr_output = test_process.stderr.read()
                    print_warning(
                        f"⚠️  Server startup test inconclusive: {stderr_output}"
                    )

            except subprocess.TimeoutExpired:
                test_process.terminate()
                print_success("✅ MCP server is responsive")

            print_success("🎉 MCP integration test completed!")
            print_info("You can now use the vector search tools in Claude Code.")

        except subprocess.TimeoutExpired:
            print_error("Timeout testing MCP server")
            raise typer.Exit(1)

    except Exception as e:
        print_error(f"Test failed: {e}")
        raise typer.Exit(1)


@mcp_app.command("remove")
def remove_mcp_integration(
    ctx: typer.Context,
    server_name: str = typer.Option(
        "mcp-vector-search", "--name", help="Name of the MCP server to remove"
    ),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
) -> None:
    """Remove MCP integration from the current project.

    Removes the server configuration from .mcp.json in the project root.
    """
    try:
        # Get project root
        project_root = ctx.obj.get("project_root") or Path.cwd()
        mcp_config_path = project_root / ".mcp.json"

        # Check if .mcp.json exists
        if not mcp_config_path.exists():
            print_warning(f"No .mcp.json found at {mcp_config_path}")
            return

        # Load configuration
        with open(mcp_config_path) as f:
            config = json.load(f)

        # Check if server exists in configuration
        if "mcpServers" not in config or server_name not in config["mcpServers"]:
            print_warning(f"MCP server '{server_name}' not found in .mcp.json")
            return

        # Confirm removal
        if not confirm:
            confirmed = typer.confirm(
                f"Remove MCP server '{server_name}' from .mcp.json?"
            )
            if not confirmed:
                print_info("Removal cancelled.")
                return

        # Remove the MCP server from configuration
        print_info(f"Removing MCP server '{server_name}' from .mcp.json...")

        del config["mcpServers"][server_name]

        # Clean up empty mcpServers section
        if not config["mcpServers"]:
            del config["mcpServers"]

        # Write updated configuration
        with open(mcp_config_path, "w") as f:
            json.dump(config, f, indent=2)

        print_success(f"✅ MCP server '{server_name}' removed from .mcp.json!")
        print_info("The server is no longer available for this project")

    except Exception as e:
        print_error(f"Removal failed: {e}")
        raise typer.Exit(1)


@mcp_app.command("status")
def show_mcp_status(
    ctx: typer.Context,
    server_name: str = typer.Option(
        "mcp-vector-search",
        "--name",
        help="Name of the MCP server to check",
        rich_help_panel="📁 Configuration",
    ),
) -> None:
    """📊 Show MCP integration status.

    Displays comprehensive status of MCP integration including Claude Code availability,
    server configuration, and project status.

    [bold cyan]Examples:[/bold cyan]

    [green]Check integration status:[/green]
        $ mcp-vector-search mcp status

    [green]Check specific server:[/green]
        $ mcp-vector-search mcp status --name my-search-server

    [dim]💡 Tip: Use this to verify Claude Code can detect the MCP server.[/dim]
    """
    try:
        # Check if Claude Code is available
        claude_available = check_claude_code_available()

        # Create status panel
        status_lines = []

        if claude_available:
            status_lines.append("✅ Claude Code: Available")
        else:
            status_lines.append("❌ Claude Code: Not available")
            status_lines.append("   Install from: https://claude.ai/download")

        # Check project configuration
        project_root = ctx.obj.get("project_root") or Path.cwd()
        mcp_config_path = project_root / ".mcp.json"
        if mcp_config_path.exists():
            with open(mcp_config_path) as f:
                project_config = json.load(f)

            if (
                "mcpServers" in project_config
                and server_name in project_config["mcpServers"]
            ):
                status_lines.append(
                    f"✅ Project Config (.mcp.json): Server '{server_name}' installed"
                )
                server_info = project_config["mcpServers"][server_name]
                if "command" in server_info:
                    status_lines.append(f"   Command: {server_info['command']}")
                if "args" in server_info:
                    status_lines.append(f"   Args: {' '.join(server_info['args'])}")
                if "env" in server_info:
                    file_watching = server_info["env"].get(
                        "MCP_ENABLE_FILE_WATCHING", "true"
                    )
                    if file_watching.lower() in ("true", "1", "yes", "on"):
                        status_lines.append("   File Watching: ✅ Enabled")
                    else:
                        status_lines.append("   File Watching: ❌ Disabled")
            else:
                status_lines.append(
                    f"❌ Project Config (.mcp.json): Server '{server_name}' not found"
                )
        else:
            status_lines.append("❌ Project Config (.mcp.json): Not found")

        # Check project status
        project_root = ctx.obj.get("project_root") or Path.cwd()
        project_manager = ProjectManager(project_root)

        if project_manager.is_initialized():
            status_lines.append(f"✅ Project: Initialized at {project_root}")
        else:
            status_lines.append(f"❌ Project: Not initialized at {project_root}")

        # Display status
        panel = Panel(
            "\n".join(status_lines), title="MCP Integration Status", border_style="blue"
        )
        console.print(panel)

    except Exception as e:
        print_error(f"Status check failed: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    mcp_app()
