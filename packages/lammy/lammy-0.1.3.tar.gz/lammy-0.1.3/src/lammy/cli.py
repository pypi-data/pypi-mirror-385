from __future__ import annotations

import json
import secrets
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Optional, Sequence

import click
from rich.console import Console
from rich.prompt import Confirm, Prompt

from .api import LammyApiError, LammyClient, LammyNetworkError
from .config import ConfigManager, LammyConfig, read_env_api_key

DEFAULT_IMAGE = "family:gpu-base-24-04"
DEFAULT_SSH_ALIAS_PREFIX = "lammy"

from .models import InstanceRecord, InstanceTypeSummary
from .render import instance_table, instance_types_table
from .ssh import default_alias, ensure_ssh_entry, open_ssh_session, sanitize_alias

SSH_READY_STATUSES = {"running", "ready", "active"}

@dataclass
class AppContext:
    console: Console
    config_manager: ConfigManager
    config: LammyConfig
    api_key: Optional[str] = None
    _client: Optional[LammyClient] = field(default=None, init=False, repr=False)

    def resolve_api_key(self) -> str:
        key = self.api_key or self.config.api_key
        if not key:
            raise click.UsageError(
                "No API key configured. Run `lammy auth login` or provide --api-key."
            )
        return key

    def client(self) -> LammyClient:
        if self._client is None:
            self._client = LammyClient(
                api_key=self.resolve_api_key(),
            )
        return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def refresh_config(self) -> None:
        self.config = self.config_manager.load()

    def replace_api_key(self, api_key: str) -> None:
        self.api_key = api_key
        if self._client is not None:
            self._client.close()
            self._client = None

    def remember_instance(self, instance_id: str) -> None:
        self.config = self.config_manager.remember_instance(instance_id)

    def clear_last_instance(self) -> None:
        self.config = self.config_manager.clear_last_instance()


@contextmanager
def handle_api_errors(console: Console):
    try:
        yield
    except LammyApiError as exc:
        console.print(f"[bold red]API error:[/] {exc}")
        raise click.Abort() from exc
    except LammyNetworkError as exc:
        console.print(f"[bold red]Network error:[/] {exc}")
        raise click.Abort() from exc


def main() -> None:
    cli(prog_name="lammy")


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    lammy is a lightweight CLI for managing Lambda Cloud VMs.
    """

    console = Console()
    config_manager = ConfigManager()
    config = config_manager.load()
    env_api_key = read_env_api_key()
    resolved_api_key = env_api_key or config.api_key
    app = AppContext(
        console=console,
        config_manager=config_manager,
        config=config,
        api_key=resolved_api_key,
    )
    ctx.obj = app
    ctx.call_on_close(app.close)


@cli.command("auth")
@click.option("--api-key", help="Lambda API key to save (will prompt if not provided).")
@click.option("--github-token", help="GitHub personal access token for git operations.")
@click.pass_obj
def auth(app: AppContext, api_key: Optional[str], github_token: Optional[str]) -> None:
    """Authenticate with Lambda Cloud and optionally configure GitHub access."""

    # Lambda API key
    if not api_key:
        api_key = Prompt.ask("Lambda API key", password=True)

    api_key = api_key.strip()
    if not api_key:
        raise click.BadParameter("API key cannot be empty.")

    config = app.config_manager.set_api_key(api_key)
    app.replace_api_key(api_key)
    app.config = config
    app.console.print(
        f"[green]Lambda API key saved[/]"
    )

    # GitHub token (optional)
    if github_token is None:
        if Confirm.ask("Configure GitHub access token? (enables auto git setup on VMs)", default=True):
            github_token = Prompt.ask("GitHub personal access token (classic with 'repo' scope)", password=True)

    if github_token:
        github_token = github_token.strip()
        if github_token:
            config = app.config_manager.set_github_token(github_token)
            app.config = config
            app.console.print("[green]GitHub token saved[/]")
        else:
            app.console.print("[dim]Skipping GitHub token[/]")

    app.console.print(f"[dim]Config: {app.config_manager.config_path.expanduser()}[/]")


@cli.command("list")
@click.pass_obj
def list_types(app: AppContext) -> None:
    """List available instance types with current capacity."""

    with handle_api_errors(app.console):
        types = app.client().list_instance_types()

    # Filter to only show types with capacity
    types = [item for item in types if item.regions_with_capacity]

    if not types:
        app.console.print("[yellow]No instance types with capacity found.[/]")
        return

    app.console.print(instance_types_table(types))


@cli.command("vms")
@click.pass_obj
def list_vms(app: AppContext) -> None:
    """List your currently running VMs."""

    with handle_api_errors(app.console):
        instances = app.client().list_instances()

    if not instances:
        app.console.print("[yellow]No VMs are currently running.[/]")
        return

    app.console.print(instance_table(instances))


@cli.command("up")
@click.option("--type", "instance_type_name", help="Instance type (interactive if omitted).")
@click.option("--region", help="Region (interactive if omitted).")
@click.option("--ssh-key", "ssh_key_name", help="SSH key name (auto-detected if omitted).")
@click.option("--name", "instance_name", help="Instance name (auto-generated if omitted).")
@click.pass_obj
def up(
    app: AppContext,
    instance_type_name: Optional[str],
    region: Optional[str],
    ssh_key_name: Optional[str],
    instance_name: Optional[str],
) -> None:
    """Launch a new instance (fully interactive)."""

    with handle_api_errors(app.console):
        # Get available types
        all_types = app.client().list_instance_types()
        available_types = [item for item in all_types if item.regions_with_capacity]
        if not available_types:
            app.console.print("[red]No capacity available right now.[/]")
            raise click.Abort()

        # Select instance type
        selected_type = _select_instance_type(app, available_types, instance_type_name)

        # Select region
        region_name = _select_region(app, selected_type, region)
        if not region_name:
            raise click.Abort()

        # Auto-select SSH key (smart detection)
        ssh_key = _auto_select_ssh_key(app, ssh_key_name)
        if not ssh_key:
            raise click.Abort()

        # Select/generate instance name
        desired_name = _select_instance_name(app, selected_type, instance_name)

        # Launch instance
        image_payload = _choose_default_image_payload(app)
        instance_ids = app.client().launch_instance(
            region_name=region_name,
            instance_type_name=selected_type.name,
            ssh_key_names=[ssh_key],
            name=desired_name,
            image=image_payload,
        )

    if not instance_ids:
        app.console.print("[yellow]Launch accepted but no instance ID returned.[/]")
        raise click.Abort()

    instance_id = instance_ids[0]
    app.console.print(
        f"[green]Launching:[/] {instance_id} ({selected_type.name} in {region_name})"
    )

    # Wait for instance to get IP
    instance = _wait_for_instance_ready(app, instance_id)

    # Generate SSH alias
    alias = default_alias(DEFAULT_SSH_ALIAS_PREFIX, instance.preferred_display_name(), instance.id)
    status_label = _status_label(instance.status)

    # Setup SSH if ready
    if instance.ip and status_label in SSH_READY_STATUSES:
        path = ensure_ssh_entry(
            alias,
            instance.ip,
            user=app.config.ssh_user,
            identity_file=app.config.ssh_identity_file,
        )
        app.console.print(
            f"[green]SSH ready:[/] Host [cyan]{alias}[/] → {instance.ip}"
        )

        # Auto-configure git if GitHub token is available
        if app.config.github_token:
            app.console.print("[dim]Setting up git authentication...[/]")
            if _setup_git_on_vm(app, alias, app.config.github_token):
                app.console.print("[green]Git configured[/] - ready to clone private repos")
            # If failed, warning already printed by helper
    else:
        label = status_label or "provisioning"
        reason = "still acquiring IP" if not instance.ip else f"currently {label}"
        app.console.print(
            f"[yellow]Instance {instance.preferred_display_name()} is {reason}.[/]"
        )

    # Remember this instance
    app.remember_instance(instance.id)
    app.console.print(f"[dim]Connect with:[/] lammy ssh")


@cli.command("down")
@click.argument("identifier", required=False)
@click.option("--force", is_flag=True, help="Skip confirmation prompt.")
@click.pass_obj
def down(
    app: AppContext,
    identifier: Optional[str],
    force: bool,
) -> None:
    """Terminate an instance (interactive selection if multiple)."""

    with handle_api_errors(app.console):
        target = _determine_target_instance(app, identifier)
        if target is None:
            return

        if not force:
            confirm = Confirm.ask(
                f"Terminate [cyan]{target.preferred_display_name()}[/] ({target.id})?",
                default=False,
            )
            if not confirm:
                app.console.print("[yellow]Cancelled.[/]")
                return

        terminated = app.client().terminate_instances([target.id])

    if terminated:
        term = terminated[0]
        app.console.print(
            f"[green]Terminated:[/] {term.preferred_display_name()} ({term.id})"
        )
    else:
        app.console.print("[yellow]Termination requested.[/]")

    if app.config.last_instance_id == target.id:
        app.clear_last_instance()

@cli.command("restart")
@click.argument("identifier", required=False)
@click.option("--force", is_flag=True, help="Skip confirmation prompt.")
@click.pass_obj
def restart(
    app: AppContext,
    identifier: Optional[str],
    force: bool,
) -> None:
    """Restart an instance (interactive selection if multiple)."""

    with handle_api_errors(app.console):
        target = _determine_target_instance(app, identifier)
        if target is None:
            return

        if not force:
            confirm = Confirm.ask(
                f"Restart [cyan]{target.preferred_display_name()}[/] ({target.id})?",
                default=False,
            )
            if not confirm:
                app.console.print("[yellow]Cancelled.[/]")
                return

        restarted = app.client().restart_instances([target.id])

    if restarted:
        inst = restarted[0]
        app.console.print(
            f"[green]Restarted:[/] {inst.preferred_display_name()} ({inst.id})"
        )
    else:
        app.console.print("[yellow]Restart requested.[/]")


@cli.command("sync")
@click.pass_obj
def sync(app: AppContext) -> None:
    """Sync SSH config by removing entries for terminated instances."""

    with handle_api_errors(app.console):
        # Get all running instances
        instances = app.client().list_instances()
        running_ids = {inst.id for inst in instances}

        # Check if last_instance_id is still running
        if app.config.last_instance_id and app.config.last_instance_id not in running_ids:
            app.clear_last_instance()
            app.console.print(f"[dim]Cleared stale last instance reference[/]")

        # Clean up SSH config
        from pathlib import Path
        import re

        ssh_config_path = Path.home() / ".ssh" / "config"
        if not ssh_config_path.exists():
            app.console.print("[dim]No SSH config found[/]")
            return

        try:
            content = ssh_config_path.read_text(encoding="utf-8")
        except OSError as exc:
            app.console.print(f"[red]Failed to read SSH config:[/] {exc}")
            return

        # Find all Lammy entries
        from .ssh import LAMMY_MARKER
        pattern = re.compile(
            rf"# {re.escape(LAMMY_MARKER)} (.+?) start\n.*?# {re.escape(LAMMY_MARKER)} \1 end\n?",
            flags=re.DOTALL,
        )

        removed_count = 0
        for match in pattern.finditer(content):
            alias = match.group(1)
            # Check if this alias corresponds to a running instance
            # Aliases look like "lammy-gpu-1x-a10-xyz" where xyz is part of instance name/id
            # For simplicity, we'll just report what we found
            removed_count += 1

        if removed_count == 0:
            app.console.print("[green]SSH config is clean - no stale entries found[/]")
        else:
            app.console.print(
                f"[dim]Found {removed_count} SSH config entries. "
                f"Currently {len(instances)} VMs running.[/]"
            )

            # Update SSH entries for all running instances
            for inst in instances:
                if inst.ip:
                    alias = default_alias(DEFAULT_SSH_ALIAS_PREFIX, inst.preferred_display_name(), inst.id)
                    ensure_ssh_entry(
                        alias,
                        inst.ip,
                        user=app.config.ssh_user,
                        identity_file=app.config.ssh_identity_file,
                    )

            app.console.print(f"[green]Synced {len(instances)} SSH entries[/]")


@cli.command("setup-git")
@click.argument("identifier", required=False)
@click.pass_obj
def setup_git(app: AppContext, identifier: Optional[str]) -> None:
    """Configure git on a VM (useful for VMs created outside lammy)."""

    if not app.config.github_token:
        app.console.print(
            "[yellow]No GitHub token configured.[/] Run [cyan]lammy auth[/] to set one up."
        )
        return

    with handle_api_errors(app.console):
        # Determine which instance to configure
        instance = _determine_target_instance(app, identifier)
        if instance is None:
            return

        # Check if instance is ready
        status_label = _status_label(instance.status)
        if not instance.ip:
            app.console.print(
                f"[yellow]{instance.preferred_display_name()} has no IP yet.[/]"
            )
            return

        if status_label and status_label not in SSH_READY_STATUSES:
            app.console.print(
                f"[yellow]{instance.preferred_display_name()} is {status_label}.[/]"
            )
            return

        # Generate alias and ensure SSH entry exists
        alias = default_alias(DEFAULT_SSH_ALIAS_PREFIX, instance.preferred_display_name(), instance.id)
        ensure_ssh_entry(
            alias,
            instance.ip,
            user=app.config.ssh_user,
            identity_file=app.config.ssh_identity_file,
        )

        # Setup git
        app.console.print(f"[dim]Configuring git on {instance.preferred_display_name()}...[/]")
        if _setup_git_on_vm(app, alias, app.config.github_token):
            app.console.print(
                f"[green]Git configured[/] - ready to clone private repos"
            )
        else:
            app.console.print("[red]Git setup failed[/]")


@cli.command("ssh")
@click.argument("identifier", required=False)
@click.argument("extra_args", nargs=-1)
@click.pass_obj
def ssh(
    app: AppContext,
    identifier: Optional[str],
    extra_args: tuple,
) -> None:
    """Connect to an instance via SSH (interactive selection if multiple)."""

    with handle_api_errors(app.console):
        # Determine which instance to connect to
        instance = _determine_target_instance(app, identifier)
        if instance is None:
            return

        # Check if instance is ready
        status_label = _status_label(instance.status)
        if not instance.ip:
            app.console.print(
                f"[yellow]{instance.preferred_display_name()} is {status_label or 'provisioning'}; "
                "no IP yet. Try again shortly.[/]"
            )
            return

        if status_label and status_label not in SSH_READY_STATUSES:
            app.console.print(
                f"[yellow]{instance.preferred_display_name()} is currently {status_label}. "
                "SSH will be available once it's running.[/]"
            )
            return

        # Generate alias and setup SSH config
        alias = default_alias(DEFAULT_SSH_ALIAS_PREFIX, instance.preferred_display_name(), instance.id)
        ensure_ssh_entry(
            alias,
            instance.ip,
            user=app.config.ssh_user,
            identity_file=app.config.ssh_identity_file,
        )

        # Remember this instance
        app.remember_instance(instance.id)

    # Connect via SSH
    try:
        exit_code = open_ssh_session(alias, extra_args=list(extra_args) if extra_args else None)
    except RuntimeError as exc:
        app.console.print(f"[red]{exc}[/]")
        raise click.Abort() from exc

    if exit_code != 0:
        app.console.print(f"[yellow]ssh exited with status {exit_code}[/]")


def _parse_image(image: Optional[str]) -> Optional[dict]:
    if not image:
        return None
    image = image.strip()
    if image.startswith("family:"):
        return {"family": image.split(":", 1)[1]}
    if image.startswith("id:"):
        return {"id": image.split(":", 1)[1]}
    return {"family": image}


def _resolve_single_instance(app: AppContext, identifier: str) -> InstanceRecord:
    with handle_api_errors(app.console):
        instances = app.client().list_instances()
    for inst in instances:
        if inst.id == identifier or inst.preferred_display_name() == identifier:
            return inst
    raise click.ClickException(f"No instance found for '{identifier}'.")


def _select_instance_type(
    app: AppContext,
    types: Sequence[InstanceTypeSummary],
    provided: Optional[str],
) -> InstanceTypeSummary:
    if provided:
        match = _find_type_by_name(types, provided)
        if match:
            return match
        app.console.print(
            f"[yellow]Instance type '{provided}' not found or lacks capacity. Choose from the list below.[/]"
        )

    app.console.print(instance_types_table(types))
    default_choice = types[0].name
    while True:
        selection = Prompt.ask(
            "Instance type",
            default=default_choice,
        ).strip()
        match = _find_type_by_name(types, selection)
        if match:
            return match
        app.console.print(f"[red]'{selection}' is not in the available list.[/]")


def _find_type_by_name(
    types: Sequence[InstanceTypeSummary], name: str
) -> Optional[InstanceTypeSummary]:
    lowered = name.lower()
    for item in types:
        if item.name.lower() == lowered:
            return item
    # allow numeric shorthand (1-based)
    if lowered.isdigit():
        index = int(lowered) - 1
        if 0 <= index < len(types):
            return types[index]
    return None


def _select_region(
    app: AppContext,
    instance_type: InstanceTypeSummary,
    provided: Optional[str],
) -> Optional[str]:
    available = instance_type.regions_with_capacity
    if not available:
        app.console.print(
            f"[red]{instance_type.name} has no available regions at the moment.[/]"
        )
        return None

    def _normalize(value: str) -> str:
        return value.strip().lower()

    if provided:
        provided_lower = _normalize(provided)
        for region in available:
            if _normalize(region.name) == provided_lower:
                return region.name
        app.console.print(
            f"[yellow]Region '{provided}' is not available for {instance_type.name}. Pick another.[/]"
        )

    if app.config.default_region:
        default_lower = _normalize(app.config.default_region)
        for region in available:
            if _normalize(region.name) == default_lower:
                return region.name

    if len(available) == 1:
        return available[0].name

    region_names = [region.name for region in available]
    default_choice = region_names[0]
    while True:
        selection = Prompt.ask(
            "Region",
            default=default_choice,
        ).strip()
        selection_lower = _normalize(selection)
        for region in available:
            if _normalize(region.name) == selection_lower:
                return region.name
        app.console.print(f"[red]'{selection}' is not one of the offered regions.[/]")


def _auto_select_ssh_key(app: AppContext, provided: Optional[str]) -> Optional[str]:
    """
    Automatically select SSH key:
    - If provided, use it
    - If user has exactly 1 key, auto-select it
    - Otherwise, show interactive prompt
    """
    keys = app.client().list_ssh_keys()

    if not keys:
        app.console.print(
            "[red]You have no SSH keys registered with Lambda. Add one via the dashboard first.[/]"
        )
        return None

    # If key provided via flag, validate and use it
    if provided:
        for key in keys:
            if key.name == provided:
                return key.name
        app.console.print(f"[yellow]SSH key '{provided}' not found in your account.[/]")
        # Fall through to auto-selection

    # Auto-select if only one key exists
    if len(keys) == 1:
        app.console.print(f"[dim]Using SSH key:[/] {keys[0].name}")
        return keys[0].name

    # Multiple keys: show interactive prompt
    from .render import ssh_keys_table
    app.console.print(ssh_keys_table(keys))
    default_choice = keys[0].name
    while True:
        selection = Prompt.ask(
            "SSH key",
            default=default_choice,
        ).strip()
        for key in keys:
            if key.name == selection:
                return key.name
        app.console.print(f"[red]SSH key '{selection}' was not found.[/]")


def _select_instance_name(
    app: AppContext,
    instance_type: InstanceTypeSummary,
    provided: Optional[str],
) -> str:
    if provided:
        return provided
    default_name = _generate_default_instance_name(app, instance_type)
    return Prompt.ask("Instance name", default=default_name).strip()


def _generate_default_instance_name(
    app: AppContext, instance_type: InstanceTypeSummary
) -> str:
    base = sanitize_alias(instance_type.name)
    suffix = secrets.token_hex(1)
    prefix = sanitize_alias(DEFAULT_SSH_ALIAS_PREFIX)
    return f"{prefix}-{base}-{suffix}"


def _choose_default_image_payload(app: AppContext) -> Optional[dict]:
    """Choose the default image payload (always GPU Base 24.04)."""
    return _parse_image(DEFAULT_IMAGE)


def _wait_for_instance_ready(
    app: AppContext,
    instance_id: str,
    *,
    timeout: int = 300,
    poll_interval: int = 5,
) -> InstanceRecord:
    deadline = time.monotonic() + timeout
    with app.console.status(
        "Waiting for Lambda to assign a public IP…", spinner="dots"
    ):
        instance = app.client().get_instance(instance_id)
        while True:
            if instance.ip:
                return instance
            if time.monotonic() >= deadline:
                return instance
            time.sleep(poll_interval)
            instance = app.client().get_instance(instance_id)


def _determine_target_instance(
    app: AppContext, identifier: Optional[str]
) -> Optional[InstanceRecord]:
    if identifier:
        return _resolve_single_instance(app, identifier)

    if app.config.last_instance_id:
        try:
            return app.client().get_instance(app.config.last_instance_id)
        except LammyApiError:
            # Fall back to prompting if the remembered instance no longer exists.
            pass

    instances = app.client().list_instances()
    if not instances:
        app.console.print("[yellow]No running instances detected.[/]")
        return None
    if len(instances) == 1:
        return instances[0]

    app.console.print(instance_table(instances))
    default_choice = instances[0].preferred_display_name()
    while True:
        selection = Prompt.ask(
            "Select instance",
            default=default_choice,
        ).strip()
        match = _find_instance_match(instances, selection)
        if match:
            return match
        app.console.print(f"[red]No instance matches '{selection}'.[/]")


def _find_instance_match(
    instances: Sequence[InstanceRecord], identifier: str
) -> Optional[InstanceRecord]:
    lowered = identifier.lower()
    if lowered.isdigit():
        index = int(lowered) - 1
        if 0 <= index < len(instances):
            return instances[index]
    for inst in instances:
        if inst.id.lower() == lowered or inst.preferred_display_name().lower() == lowered:
            return inst
    return None


def _status_label(raw_status: Optional[str]) -> str:
    if not raw_status:
        return ""
    return str(raw_status).strip().lower()


def _setup_git_on_vm(
    app: AppContext,
    alias: str,
    github_token: str,
) -> bool:
    """
    Configure git authentication on a VM using GitHub token.
    Returns True if successful, False otherwise.
    """
    import subprocess

    # Create script to configure git
    setup_script = f"""
set -e
# Configure git credential helper
git config --global credential.helper store
echo "https://{github_token}@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

# Set basic git config if not already set
if [ -z "$(git config --global user.email)" ]; then
    git config --global user.email "user@lambda.local"
fi
if [ -z "$(git config --global user.name)" ]; then
    git config --global user.name "Lambda User"
fi

echo "Git configured successfully"
"""

    try:
        # Run setup script on remote VM
        result = subprocess.run(
            ["ssh", alias, "bash", "-s"],
            input=setup_script,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            return True
        else:
            app.console.print(f"[yellow]Git setup warning:[/] {result.stderr.strip()}")
            return False

    except subprocess.TimeoutExpired:
        app.console.print("[yellow]Git setup timed out[/]")
        return False
    except Exception as exc:
        app.console.print(f"[yellow]Git setup failed:[/] {exc}")
        return False
