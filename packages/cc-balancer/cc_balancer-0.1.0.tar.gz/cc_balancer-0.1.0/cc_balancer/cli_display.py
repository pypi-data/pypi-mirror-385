"""
CLI display utilities for CC-Balancer.

Provides beautiful ASCII art banners and formatted configuration displays.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cc_balancer.config import AppConfig

console = Console()

# ASCII Art Banner
BANNER = r"""
   __________      ____        __
  / ____/ __ \    / __ )____ _/ /___ _____  ________  _____
 / /   / /   ____/ __  / __ `/ / __ `/ __ \/ ___/ _ \/ ___/
/ /___/ /___/___/ /_/ / /_/ / / /_/ / / / / /__/  __/ /
\____/\____/   /_____/\__,_/_/\__,_/_/ /_/\___/\___/_/
"""

SUBTITLE = "Intelligent Proxy for Claude Code with Automatic Failover & Load Balancing"


def print_banner() -> None:
    """Print the application banner with ASCII art."""
    console.print()
    console.print(BANNER, style="bold cyan")
    console.print()
    console.print(SUBTITLE, style="italic bright_white", justify="center")
    console.print("=" * 90, style="cyan")
    console.print()


def print_config_info(config: AppConfig, host: str, port: int, reload: bool) -> None:
    """
    Print formatted configuration information.

    Args:
        config: Application configuration
        host: Server host
        port: Server port
        reload: Whether auto-reload is enabled
    """
    # Server Configuration Panel
    server_info = Table.grid(padding=(0, 2))
    server_info.add_column(style="bold cyan", justify="right")
    server_info.add_column(style="bright_white")

    server_info.add_row("Host:", host)
    server_info.add_row("Port:", str(port))
    server_info.add_row("Log Level:", config.server.log_level.upper())
    server_info.add_row(
        "Auto-Reload:",
        "[green]✓ Enabled[/green]" if reload else "[dim]✗ Disabled[/dim]",
    )

    console.print(
        Panel(
            server_info,
            title="[bold]🚀 Server Configuration[/bold]",
            border_style="cyan",
            padding=(1, 2),
        )
    )

    # Routing & Error Handling Configuration Panel
    routing_info = Table.grid(padding=(0, 2))
    routing_info.add_column(style="bold magenta", justify="right")
    routing_info.add_column(style="bright_white")

    routing_info.add_row("Strategy:", config.routing.strategy.upper())
    routing_info.add_row("Failure Threshold:", str(config.error_handling.failure_threshold))
    routing_info.add_row(
        "Recovery Interval:", f"{config.error_handling.recovery_interval_seconds}s"
    )
    routing_info.add_row("Cache Enabled:", _format_bool(config.cache.enabled))
    routing_info.add_row("Cache TTL:", f"{config.cache.ttl_seconds}s")

    console.print(
        Panel(
            routing_info,
            title="[bold]🔀 Routing & Resilience[/bold]",
            border_style="magenta",
            padding=(1, 2),
        )
    )

    # Providers Configuration Table
    providers_table = Table(
        show_header=True,
        header_style="bold yellow",
        border_style="yellow",
        title="[bold]🔌 Provider Configuration[/bold]",
        title_style="bold yellow",
        padding=(0, 1),
    )

    providers_table.add_column("Name", style="cyan", no_wrap=True)
    providers_table.add_column("Base URL", style="bright_white")
    providers_table.add_column("Auth Type", style="magenta")
    providers_table.add_column("Weight", justify="center", style="green")
    providers_table.add_column("Priority", justify="center", style="blue")
    providers_table.add_column("Timeout", justify="center", style="yellow")

    for provider in config.providers:
        providers_table.add_row(
            provider.name,
            _truncate_url(str(provider.base_url)),
            provider.auth_type.upper(),
            str(provider.weight),
            str(provider.priority),
            f"{provider.timeout_seconds}s",
        )

    console.print(providers_table)
    console.print()


def print_startup_success(provider_count: int, host: str, port: int) -> None:
    """
    Print startup success message with Claude Code configuration guide.

    Args:
        provider_count: Number of registered providers
        host: Server host address
        port: Server port
    """
    message = Text()
    message.append("✓ ", style="bold green")
    message.append("CC-Balancer started successfully with ", style="bright_white")
    message.append(str(provider_count), style="bold cyan")
    message.append(" provider(s)", style="bright_white")

    console.print()
    console.print(
        Panel(
            message,
            border_style="green",
            padding=(0, 2),
        )
    )
    console.print()


def print_claude_code_config(host: str, port: int) -> None:
    """
    Print Claude Code configuration instructions.

    Args:
        host: Server host address
        port: Server port
    """
    # Determine the base URL
    if host in ("0.0.0.0", "127.0.0.1", "localhost"):
        base_url = f"http://localhost:{port}"
    else:
        base_url = f"http://{host}:{port}"

    # Create configuration table
    config_table = Table.grid(padding=(0, 2))
    config_table.add_column(style="bold yellow", justify="right", width=20)
    config_table.add_column(style="bright_white")

    config_table.add_row("Base URL:", f"[cyan]{base_url}[/cyan]")
    config_table.add_row("API Endpoint:", f"[cyan]{base_url}/v1/messages[/cyan]")
    config_table.add_row("Health Check:", f"[cyan]{base_url}/healthz[/cyan]")

    console.print(
        Panel(
            config_table,
            title="[bold]🔧 Claude Code Configuration[/bold]",
            subtitle="[dim]Add to your Claude Code settings[/dim]",
            border_style="yellow",
            padding=(1, 2),
        )
    )

    # Environment variable instructions
    env_instructions = Text()
    env_instructions.append("1. Open Claude Code Settings\n", style="bold")
    env_instructions.append("2. Navigate to ", style="bright_white")
    env_instructions.append("Anthropic API Settings\n", style="cyan")
    env_instructions.append("3. Set ", style="bright_white")
    env_instructions.append("Base URL", style="cyan")
    env_instructions.append(" to: ", style="bright_white")
    env_instructions.append(base_url, style="bold green")

    console.print()
    console.print(
        Panel(
            env_instructions,
            title="[bold]📝 Quick Setup Guide[/bold]",
            border_style="blue",
            padding=(1, 2),
        )
    )

    # Alternative: Environment variable method
    env_config = Text()
    env_config.append(
        "# Add to your shell configuration (~/.bashrc, ~/.zshrc, etc.)\n\n", style="dim"
    )
    env_config.append("export ANTHROPIC_BASE_URL=", style="bright_white")
    env_config.append(f'"{base_url}"\n', style="green")
    env_config.append("export ANTHROPIC_API_KEY=", style="bright_white")
    env_config.append('"sk-ant-your-api-key-here"', style="yellow")

    console.print()
    console.print(
        Panel(
            env_config,
            title="[bold]🌍 Alternative: Environment Variables[/bold]",
            subtitle="[dim]For command-line usage[/dim]",
            border_style="magenta",
            padding=(1, 2),
        )
    )
    console.print()


def print_error(error_type: str, message: str) -> None:
    """
    Print formatted error message.

    Args:
        error_type: Type of error (e.g., "Configuration Error")
        message: Error message
    """
    console.print()
    console.print(
        Panel(
            f"[bold red]✗ {error_type}[/bold red]\n\n{message}",
            border_style="red",
            padding=(1, 2),
        )
    )
    console.print()


def print_shutdown() -> None:
    """Print shutdown message."""
    console.print()
    console.print(
        Panel(
            "[bold yellow]⏸  CC-Balancer is shutting down...[/bold yellow]",
            border_style="yellow",
            padding=(0, 2),
        )
    )


def _format_bool(value: bool) -> str:
    """
    Format boolean value with color.

    Args:
        value: Boolean value

    Returns:
        Formatted string with color
    """
    return "[green]✓ Yes[/green]" if value else "[dim]✗ No[/dim]"


def _truncate_url(url: str, max_length: int = 50) -> str:
    """
    Truncate URL if it's too long.

    Args:
        url: URL to truncate
        max_length: Maximum length

    Returns:
        Truncated URL with ellipsis if needed
    """
    if len(url) <= max_length:
        return url
    return url[: max_length - 3] + "..."
