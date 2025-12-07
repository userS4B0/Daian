import typer
from rich import print
from rich.pretty import Pretty

from config.config_loader import ConfigLoader
from config.validator import ConfigValidator

config_app = typer.Typer(help="Configuration tools for DAIAN")


@config_app.command("show")
def show_config():
    """
    Show merged configuration as DAIAN sees it.
    """
    conf_app = ConfigLoader.load("app_settings")
    conf_user = ConfigLoader.load("user_settings")

    merged = ConfigLoader._deep_merge(conf_app, conf_user)

    print("[bold cyan]DAIAN Loaded Configuration:[/bold cyan]")
    print(Pretty(merged))


@config_app.command("check")
def check_config():
    """
    Validate configuration correctness.
    """

    merged = ConfigLoader._deep_merge(
        ConfigLoader.load("app_settings"),
        ConfigLoader.load("user_settings"),
    )

    print("[bold yellow]Validating configuration...[/bold yellow]")
    ok = ConfigValidator.validate(merged)

    if ok:
        print("[bold green]✔ Config OK[/bold green]")
    else:
        print("[bold red]✖ Problems found in configuration[/bold red]")

# FEATURE: Implement config initialization from cli entrypoint
# Implement function `daian config init` to generate default config in `~/.config/daian/user_config.yml` 
# assignees: userS4B0
# labels: priority_low, core, feature
# milestone: v1.0.0

# FEATURE: Implement config edit from cli entrypoint
# Add support for editing todoist api token config & more calendar integrations instead of modifying always the config file.
# assignees: userS4B0
# labels: priority_low, core, feature
# milestone: v1.1.0
