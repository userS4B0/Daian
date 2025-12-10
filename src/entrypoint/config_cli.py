import typer
from rich import print
from rich.pretty import Pretty

from config.config_loader import ConfigLoader
from config.validator import ConfigValidator

config_app = typer.Typer(help="Configuration tools for DAIAN")


@config_app.command("show", help="Shows current loaded Daian configuration.")
def show_config():
    """
    Show merged configuration as DAIAN sees it.
    """
    full_config = ConfigLoader.load_all()

    print("[bold cyan]DAIAN Loaded Configuration:[/bold cyan]")
    print(Pretty(full_config))


@config_app.command("check", help="Validates current loaded Daian configuration.")
def check_config():
    """
    Validate configuration correctness.
    """

    full_config = ConfigLoader.load_all()
    print("[bold yellow]Validating configuration...[/bold yellow]")

    ok = ConfigValidator.validate(full_config)

    if ok:
        print("[bold green]✔ Config OK[/bold green]")
    else:
        print("[bold red]✖ Problems found in configuration[/bold red]")


@config_app.command(
    "init", help="Initializes default DAIAN config in your user config directory."
)
def init_config(
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing config"
    ),
):
    """
    Create user's configuration files at ~/.config/daian/ only if they do not exist.
    If --force is used, they are overwritten.
    """
    import shutil
    from pathlib import Path

    # Resolve user config directory
    user_dir = Path("~/.config/daian").expanduser()
    user_dir.mkdir(parents=True, exist_ok=True)

    # Paths for user config & shipped defaults
    user_file = user_dir / "user_settings.yml"

    # shipped-in defaults from src/config
    default_dir = Path(__file__).resolve().parent  # src/config/
    default_file = default_dir / "app_settings.yml"

    print("[bold cyan]DAIAN Configuration Initialization[/bold cyan]")
    print(f"→ User config dir: [bold]{user_dir}[/bold]")

    # Check if user file already exists
    if user_file.exists() and not force:
        print(f"[yellow]Config already exists at {user_file}[/yellow]")
        print("Use --force to overwrite.")
        return

    # Copy default shipped config → user config
    # BUG: Implement dev_mode checker in config edit command
    # Implement dev_mode checker so it doesn't load testing configs & non-production configs that may affect production Daian functionalities.
    # assignees: userS4B0
    # labels: priority_medium, cli, bug
    # milestone: v1.0.1
    try:
        shutil.copy(default_file, user_file)
        print(f"[green] Default config written to[/green] [bold]{user_file}[/bold]")
    except Exception as e:
        print(f"[red] Failed to copy default config: {e}[/red]")
        raise typer.Exit(code=1)

    # Validate configuration after creation
    check_config()

    # Show final loaded configuration
    show_config()

# FEATURE: Implement config edit from cli entrypoint
# Add support for editing todoist api token config & more calendar integrations instead of modifying always the config file.
# assignees: userS4B0
# labels: priority_low, core, feature
# milestone: v1.1.0
