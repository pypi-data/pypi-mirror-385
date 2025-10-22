"""
Config commands for Clauxton CLI.

Provides commands to manage Clauxton configuration.
"""

from pathlib import Path

import click

from clauxton.core.confirmation_manager import ConfirmationManager
from clauxton.core.models import ValidationError


@click.group()
def config() -> None:
    """Manage Clauxton configuration."""
    pass


@config.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str) -> None:
    """
    Set configuration value.

    Keys:
        confirmation_mode         - Set confirmation mode (always/auto/never)
        task_import_threshold     - Set task import confirmation threshold
        task_delete_threshold     - Set task delete confirmation threshold
        kb_delete_threshold       - Set KB delete confirmation threshold
        kb_import_threshold       - Set KB import confirmation threshold

    Example:
        clauxton config set confirmation_mode always
        clauxton config set task_import_threshold 20
    """
    clauxton_dir = Path.cwd() / ".clauxton"

    if not clauxton_dir.exists():
        click.echo(
            click.style(
                "Error: Clauxton not initialized. Run 'clauxton init' first.",
                fg="red",
            )
        )
        raise click.Abort()

    cm = ConfirmationManager(clauxton_dir)

    try:
        if key == "confirmation_mode":
            if value not in ["always", "auto", "never"]:
                click.echo(
                    click.style(
                        f"Error: Invalid confirmation mode '{value}'. "
                        "Must be 'always', 'auto', or 'never'.",
                        fg="red",
                    )
                )
                raise click.Abort()
            cm.set_mode(value)  # type: ignore
            click.echo(
                click.style(
                    f"✓ Set confirmation_mode to '{value}'", fg="green"
                )
            )

        elif key.endswith("_threshold"):
            # Extract operation type from key
            # e.g., "task_import_threshold" -> "task_import"
            operation_type = key.replace("_threshold", "")

            try:
                threshold_value = int(value)
            except ValueError:
                click.echo(
                    click.style(
                        f"Error: Invalid threshold value '{value}'. Must be an integer.",
                        fg="red",
                    )
                )
                raise click.Abort()

            cm.set_threshold(operation_type, threshold_value)
            click.echo(
                click.style(
                    f"✓ Set {key} to {threshold_value}", fg="green"
                )
            )

        else:
            click.echo(
                click.style(
                    f"Error: Unknown configuration key '{key}'. "
                    "Run 'clauxton config list' to see available keys.",
                    fg="red",
                )
            )
            raise click.Abort()

    except ValidationError as e:
        click.echo(click.style(f"Error: {e}", fg="red"))
        raise click.Abort()


@config.command()
@click.argument("key")
def get(key: str) -> None:
    """
    Get configuration value.

    Example:
        clauxton config get confirmation_mode
        clauxton config get task_import_threshold
    """
    clauxton_dir = Path.cwd() / ".clauxton"

    if not clauxton_dir.exists():
        click.echo(
            click.style(
                "Error: Clauxton not initialized. Run 'clauxton init' first.",
                fg="red",
            )
        )
        raise click.Abort()

    cm = ConfirmationManager(clauxton_dir)

    if key == "confirmation_mode":
        mode = cm.get_mode()
        click.echo(mode)

    elif key.endswith("_threshold"):
        # Extract operation type from key
        operation_type = key.replace("_threshold", "")
        threshold = cm.get_threshold(operation_type)
        click.echo(threshold)

    else:
        click.echo(
            click.style(
                f"Error: Unknown configuration key '{key}'. "
                "Run 'clauxton config list' to see available keys.",
                fg="red",
            )
        )
        raise click.Abort()


@config.command()
def list() -> None:
    """
    List all configuration values.

    Example:
        clauxton config list
    """
    clauxton_dir = Path.cwd() / ".clauxton"

    if not clauxton_dir.exists():
        click.echo(
            click.style(
                "Error: Clauxton not initialized. Run 'clauxton init' first.",
                fg="red",
            )
        )
        raise click.Abort()

    cm = ConfirmationManager(clauxton_dir)
    config_dict = cm.get_all_config()

    # Display configuration
    click.echo(click.style("Clauxton Configuration", fg="cyan", bold=True))
    click.echo(click.style("=" * 40, fg="cyan"))

    # Version
    version = config_dict.get("version", "1.0")
    click.echo(f"version: {click.style(version, fg='blue')}")

    # Confirmation mode
    mode = config_dict.get("confirmation_mode", "auto")
    mode_color = "green" if mode == "auto" else "yellow"
    click.echo(f"confirmation_mode: {click.style(mode, fg=mode_color)}")

    # Thresholds
    thresholds = config_dict.get("confirmation_thresholds", {})
    if thresholds:
        click.echo("\n" + click.style("Confirmation Thresholds:", fg="cyan"))
        for op_type, threshold_value in sorted(thresholds.items()):
            threshold_key = f"{op_type}_threshold"
            click.echo(f"  {threshold_key}: {click.style(str(threshold_value), fg='blue')}")
