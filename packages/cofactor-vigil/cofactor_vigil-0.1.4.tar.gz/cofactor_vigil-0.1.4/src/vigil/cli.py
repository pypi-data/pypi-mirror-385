"""Vigil CLI - Next.js-style command interface for reproducible science."""

from __future__ import annotations

import json
import shlex
import shutil
import subprocess
from collections.abc import Iterable, Sequence  # noqa: TCH003
from dataclasses import dataclass
from datetime import UTC
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from vigil.tools import anchor as anchor_tool
from vigil.tools import doctor as doctor_tool
from vigil.tools import promote as promote_tool
from vigil.tools import verify as verify_tool
from vigil.tools import vigilurl as vigilurl_tool
from vigil.tools import workspace_spec as workspace_spec_tool

if TYPE_CHECKING:
    pass

# Package version
__version__ = "0.1.4"


def _version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"[bold cyan]Vigil CLI[/bold cyan] version [green]{__version__}[/green]")
        raise typer.Exit()


app = typer.Typer(
    help="Vigil CLI: observable, collaborative, reproducible science.",
    no_args_is_help=True,
)
ai_app = typer.Typer(help="Auto-target helpers that coordinate with MCP tools.")
ui_app = typer.Typer(help="Workbench utilities for browsing data and evidence.")
mcp_app = typer.Typer(help="Machine-Callable-Protocol server helpers.")
card_app = typer.Typer(help="Experiment and Dataset card management.")
notes_app = typer.Typer(help="Lab notebook management and templates.")

app.add_typer(ai_app, name="ai")
app.add_typer(ui_app, name="ui")
app.add_typer(mcp_app, name="mcp")
app.add_typer(card_app, name="card")
app.add_typer(notes_app, name="notes")

# Global rich console instance
console = Console()


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version information",
        is_eager=True,
    ),
) -> None:
    """Vigil CLI callback to handle global options."""
    if version:
        console.print(f"[bold cyan]Vigil CLI[/bold cyan] version [green]{__version__}[/green]")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        # No command provided, show help
        console.print(ctx.get_help())


# Rich CLI helper functions
def _print_success(message: str) -> None:
    """Print success message with rich formatting."""
    console.print(f"[bold green]✓[/bold green] {message}")


def _print_error(message: str) -> None:
    """Print error message with rich formatting."""
    console.print(f"[bold red]✗[/bold red] {message}", style="red")


def _print_warning(message: str) -> None:
    """Print warning message with rich formatting."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}", style="yellow")


def _print_info(message: str) -> None:
    """Print info message with rich formatting."""
    console.print(f"[bold cyan]ℹ[/bold cyan] {message}")


_PIPELINES: dict[str, Path] = {
    "default": Path("app/code/pipelines/Snakefile"),
    "federated": Path("app/code/pipelines/federated/Snakefile"),
}

DEFAULT_ARTIFACTS_DIR = Path("app/code/artifacts")
DEFAULT_RECEIPTS_DIR = Path("app/code/receipts")


@dataclass(slots=True)
class CommandResult:
    """Container for subprocess output."""

    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def _quote_command(cmd: Sequence[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in cmd)


def _run_command(cmd: Sequence[str]) -> CommandResult:
    process = subprocess.run(list(cmd), capture_output=True, text=True, check=False)
    return CommandResult(process.returncode, process.stdout, process.stderr)


def _echo_command(cmd: Sequence[str]) -> None:
    typer.echo(f"$ {_quote_command(cmd)}")


def _print_output(result: CommandResult) -> None:
    if result.stdout.strip():
        typer.echo(result.stdout.rstrip())
    if result.stderr.strip():
        typer.echo(result.stderr.rstrip(), err=True)


def _resolve_pipeline(name: str) -> Path:
    if name in _PIPELINES:
        return _PIPELINES[name]
    path = Path(name)
    if not path.exists():
        raise typer.BadParameter(
            f"Unknown pipeline '{name}'. Provide a valid name or Snakefile path."
        )
    return path


def _ensure_targets(targets: Iterable[str]) -> list[str]:
    resolved = [target for target in (str(item).strip() for item in targets) if target]
    return resolved or ["all"]


def _check_gpu_available() -> bool:
    """Check if a GPU is available via nvidia-smi."""
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.SubprocessError, subprocess.TimeoutExpired):
        return False


def _validate_profile(profile: str | None, warn_gpu: bool = True) -> None:
    """Validate that the requested profile exists.

    Checks for profile YAML files in:
    1. app/code/configs/profiles/{profile}.yaml (project-level)
    2. Standard blessed profiles (cpu, gpu, slurm, tee)

    Args:
        profile: Profile name to validate
        warn_gpu: If True, warn when using gpu profile without GPU

    Raises:
        typer.Exit: If profile is specified but not found
    """
    if not profile:
        return  # No profile specified, use Snakemake defaults

    # Check project-level profiles first
    project_profile = Path("app/code/configs/profiles") / f"{profile}.yaml"
    if project_profile.exists():
        # Profile found, check GPU if needed
        if warn_gpu and profile == "gpu" and not _check_gpu_available():
            _print_warning("GPU profile selected but no GPU detected via nvidia-smi")
            console.print("[dim]Run 'vigil doctor' to check GPU availability[/dim]")
            console.print("[dim]Consider using 'cpu' profile if no GPU is available[/dim]")
        return

    # Check for blessed profiles (these might be in package or system locations)
    blessed_profiles = {"cpu", "gpu", "slurm", "tee"}
    if profile in blessed_profiles:
        # GPU availability warning for blessed gpu profile
        if warn_gpu and profile == "gpu" and not _check_gpu_available():
            _print_warning("GPU profile selected but no GPU detected via nvidia-smi")
            console.print("[dim]Run 'vigil doctor' to check GPU availability[/dim]")
            console.print("[dim]Consider using 'cpu' profile if no GPU is available[/dim]")
        return  # Snakemake will find it via --profile

    # Profile not found
    _print_error(f"Profile '{profile}' not found")
    console.print("\n[bold]Available profiles:[/bold]")

    # List project profiles
    profiles_dir = Path("app/code/configs/profiles")
    if profiles_dir.exists():
        project_profiles = sorted(p.stem for p in profiles_dir.glob("*.yaml"))
        if project_profiles:
            console.print(f"  [cyan]Project profiles:[/cyan] {', '.join(project_profiles)}")

    # List blessed profiles
    console.print(f"  [cyan]Blessed profiles:[/cyan] {', '.join(sorted(blessed_profiles))}")
    console.print("\n[dim]Run 'vigil doctor' to check profile configuration[/dim]")
    console.print("[dim]See docs/profiles.md for profile documentation[/dim]")
    raise typer.Exit(code=1)


def _snakemake_base(targets: Iterable[str], profile: str | None, pipeline: str) -> list[str]:
    _validate_profile(profile)
    snakefile = _resolve_pipeline(pipeline)
    base = ["uv", "run", "snakemake", "-s", snakefile.as_posix()]
    base.extend(_ensure_targets(targets))
    if profile:
        base.extend(["--profile", profile])
    return base


def _find_vigil_root() -> Path:
    """Find the Vigil project root by looking for vigil.yaml.

    Searches upward from the current directory through parent directories
    until vigil.yaml is found.

    Returns:
        Path: The project root directory containing vigil.yaml

    Raises:
        typer.Exit: If vigil.yaml is not found in any parent directory
    """
    current = Path.cwd()
    for directory in [current, *current.parents]:
        if (directory / "vigil.yaml").exists():
            return directory

    # Not in a Vigil project - provide clear, actionable error
    _print_error(
        "Not in a Vigil project. This command must be run from a directory "
        "containing vigil.yaml or any subdirectory within a Vigil project."
    )
    console.print("\n[bold]To fix this:[/bold]")
    console.print("  • [cyan]cd[/cyan] to an existing Vigil project directory")
    console.print("  • Or create a new project: [cyan]vigil new <template> <path>[/cyan]")
    console.print("  • List available templates: [cyan]vigil new --list[/cyan]")
    raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"[bold cyan]Vigil CLI[/bold cyan] version [green]{__version__}[/green]")


def _should_ignore_file(path: str, names: list[str]) -> set[str]:
    """Filter function for shutil.copytree to exclude development artifacts.

    Excludes:
    - Python cache: __pycache__, *.pyc, *.pyo
    - Tool caches: .ruff_cache, .mypy_cache, .pytest_cache
    - Coverage: .coverage, .coverage.*, htmlcov
    - Git: .git (but keep .gitignore and .github)
    - Virtual environments: .venv, venv, env
    - Build artifacts: .snakemake, build/, dist/, *.egg-info
    - IDE: .vscode, .idea (but keep .editorconfig)
    - OS: .DS_Store, Thumbs.db
    """
    ignored = set()

    # Directories to completely exclude
    exclude_dirs = {
        "__pycache__",
        ".ruff_cache",
        ".mypy_cache",
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        ".git",
        ".venv",
        "venv",
        "env",
        ".snakemake",
        "build",
        "dist",
        ".vscode",
        ".idea",
    }

    # File patterns to exclude
    for name in names:
        # Exclude directories
        if name in exclude_dirs:
            ignored.add(name)
            continue

        # Exclude Python bytecode
        if name.endswith((".pyc", ".pyo")):
            ignored.add(name)
            continue

        # Exclude coverage files
        if name.startswith(".coverage"):
            ignored.add(name)
            continue

        # Exclude egg-info
        if name.endswith(".egg-info"):
            ignored.add(name)
            continue

        # Exclude OS files
        if name in {".DS_Store", "Thumbs.db"}:
            ignored.add(name)
            continue

    return ignored


@app.command()
def new(
    template: str | None = typer.Argument(
        None, help="Template name (imaging-starter, minimal-starter, etc.)"
    ),
    path: Path = typer.Argument(Path("."), help="Target directory for new project"),
    list_templates: bool = typer.Option(False, "--list", help="List available templates"),
) -> None:
    """Create a new Vigil project from a template."""
    # Find the vigil package installation location to locate examples/
    import vigil

    vigil_path = Path(vigil.__file__).parent
    examples_dir = vigil_path / "examples"

    if list_templates:
        if not examples_dir.exists():
            _print_error("No templates found.")
            raise typer.Exit(code=1)

        # Create rich table for templates
        table = Table(title="Available Vigil Templates", show_header=True, header_style="bold cyan")
        table.add_column("Template", style="green", width=20)
        table.add_column("Description", width=50)
        table.add_column("Features", style="dim", width=25)

        # Template metadata
        templates = {
            "imaging-starter": ("Full-featured microscopy analysis pipeline", "GPU, MCP, Workbench"),
            "minimal-starter": ("Smallest viable template for quick starts", "CPU only, Simple"),
        }

        # Add rows for templates found on disk
        for template_dir in sorted(examples_dir.iterdir()):
            if template_dir.is_dir() and not template_dir.name.startswith("."):
                desc, features = templates.get(template_dir.name, ("Custom template", ""))
                table.add_row(template_dir.name, desc, features)

        console.print(table)
        console.print("\n[dim]Usage: vigil new <template> <path>[/dim]")
        raise typer.Exit(code=0)

    if template is None:
        _print_error("Template name is required. Use --list to see available templates.")
        raise typer.Exit(code=1)

    template_dir = examples_dir / template
    if not template_dir.exists():
        _print_error(f"Template '{template}' not found. Use --list to see available templates.")
        raise typer.Exit(code=1)

    # Create target directory
    target = path.resolve()
    if target.exists() and any(target.iterdir()):
        _print_error(f"{target} already exists and is not empty.")
        raise typer.Exit(code=1)

    target.mkdir(parents=True, exist_ok=True)

    # Copy template with ignore filter to exclude development artifacts
    with console.status(f"[bold green]Creating project from '{template}'..."):
        shutil.copytree(template_dir, target, dirs_exist_ok=True, ignore=_should_ignore_file)

    _print_success("Project created successfully!")
    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  [cyan]cd {target.name}[/cyan]")
    console.print("  [cyan]uv sync[/cyan]")
    console.print("  [cyan]vigil dev[/cyan]")


@app.command()
def init(
    template: str = typer.Argument(
        ..., help="Template name (imaging-starter, minimal-starter, etc.)"
    ),
    path: Path = typer.Argument(Path("."), help="Target directory for new project"),
) -> None:
    """Create a production-ready Vigil project with pinned manifests and workspace spec."""
    from datetime import datetime

    import vigil

    vigil_path = Path(vigil.__file__).parent
    examples_dir = vigil_path / "examples"

    template_dir = examples_dir / template
    if not template_dir.exists():
        _print_error(f"Template '{template}' not found. Use 'vigil new --list' to see available templates.")
        raise typer.Exit(code=1)

    # Create target directory
    target = path.resolve()
    if target.exists() and any(target.iterdir()):
        _print_error(f"{target} already exists and is not empty.")
        raise typer.Exit(code=1)

    target.mkdir(parents=True, exist_ok=True)

    # Copy template with ignore filter to exclude development artifacts
    with console.status(f"[bold green]Creating production-ready project from '{template}'..."):
        shutil.copytree(template_dir, target, dirs_exist_ok=True, ignore=_should_ignore_file)

    # Check if template has vigil.yaml
    vigil_yaml_path = target / "vigil.yaml"
    if not vigil_yaml_path.exists():
        _print_warning("Template missing vigil.yaml. Skipping workspace spec generation.")
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"  [cyan]cd {target.name}[/cyan]")
        console.print("  [cyan]uv sync[/cyan]")
        console.print("  [cyan]vigil dev[/cyan]")
        return

    # Get git ref if in a git repo
    try:
        git_ref_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=target,
            capture_output=True,
            text=True,
            check=False,
        )
        git_ref = f"refs/heads/{git_ref_result.stdout.strip()}" if git_ref_result.returncode == 0 else "refs/heads/main"
    except Exception:
        git_ref = "refs/heads/main"

    # Generate workspace.spec.json using workspace_spec_tool
    try:
        # Use the workspace_spec module to sync capsule metadata from vigil.yaml
        spec, spec_path = workspace_spec_tool.sync_workspace_spec(target)

        # Enhance the spec with additional production-ready fields
        spec["version"] = spec.get("version", "1.0.0")
        spec["ref"] = git_ref
        spec["scopes"] = spec.get("scopes", ["preview_data", "run_target", "promote"])

        # Ensure resources has all required fields
        if "resources" not in spec:
            spec["resources"] = {}
        spec["resources"].setdefault("cpu", "2")
        spec["resources"].setdefault("memory", "4Gi")
        spec["resources"].setdefault("gpu", "0")

        spec["issuedAt"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        spec["signature"] = spec.get("signature", "UNSIGNED-DEV")

        # Copy inputs and policies from manifest
        manifest = workspace_spec_tool.load_manifest(target)
        spec["inputs"] = manifest.get("inputs", [])
        spec["policies"] = manifest.get("policies", {})

        # Write the enhanced workspace spec
        workspace_spec_tool.write_workspace_spec(spec, spec_path)

        # Success panel with detailed information
        capsule_image = spec["capsule"]["image"]
        capsule_display = capsule_image if len(capsule_image) <= 60 else f"{capsule_image[:57]}..."
        panel = Panel(
            f"[bold green]Production-ready project created![/bold green]\n\n"
            f"Location: [cyan]{target}[/cyan]\n"
            f"Template: [yellow]{template}[/yellow]\n"
            f"Workspace spec: [dim]{spec_path.relative_to(target)}[/dim]\n"
            f"Git ref: [dim]{git_ref}[/dim]\n"
            f"Capsule: [dim]{capsule_display}[/dim]",
            title="✓ Success",
            border_style="green",
        )
        console.print("\n", panel)

    except Exception as e:
        _print_error(f"Failed to generate workspace spec: {e}")
        raise typer.Exit(code=1) from None

    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  [cyan]cd {target.name}[/cyan]")
    console.print("  [cyan]uv sync[/cyan]")
    console.print("  [cyan]vigil dev[/cyan]")


@app.command()
def dev(
    profile: str | None = typer.Option(
        None,
        help=(
            "Snakemake profile to use. "
            "cpu: Local dev (2 cores, 2GB) | "
            "gpu: GPU workloads (1 GPU, 16GB) | "
            "slurm: HPC cluster | "
            "tee: Trusted execution with attestation. "
            "See docs/profiles.md for details."
        ),
    ),
    target: list[str] = typer.Option(
        None, "--target", help="Specific targets to preview (defaults to all)."
    ),
    pipeline: str = typer.Option("default", help="Pipeline to operate on (default)."),
) -> None:
    """Dry-run the DAG and emit a Suggestion Cell without mutating artifacts."""
    _find_vigil_root()  # Ensure we're in a project

    targets = _ensure_targets(target or [])
    base = _snakemake_base(targets, profile, pipeline)

    dry_cmd = [*base, "-n"]
    _echo_command(dry_cmd)
    dry_result = _run_command(dry_cmd)
    _print_output(dry_result)
    if not dry_result.ok:
        raise typer.Exit(code=dry_result.returncode)

    dag_cmd = [*base, "--dag"]
    _echo_command(dag_cmd)
    dag_result = _run_command(dag_cmd)
    _print_output(dag_result)
    if not dag_result.ok:
        raise typer.Exit(code=dag_result.returncode)

    _print_success("Pipeline dry-run successful. Ready to execute with 'vigil run'.")


@app.command()
def build(
    profile: str | None = typer.Option(
        None,
        help=(
            "Snakemake profile to use. "
            "cpu: Local dev (2 cores, 2GB) | "
            "gpu: GPU workloads (1 GPU, 16GB) | "
            "slurm: HPC cluster | "
            "tee: Trusted execution. "
            "See docs/profiles.md"
        ),
    ),
    target: list[str] = typer.Option(None, "--target", help="Targets to build (defaults to all)."),
    pipeline: str = typer.Option("default", help="Pipeline to operate on."),
    cores: int = typer.Option(4, min=1, help="Number of cores to allocate for Snakemake."),
) -> None:
    """Execute the pipeline without promotion, mirroring 'next build'."""
    _find_vigil_root()

    targets = _ensure_targets(target or [])
    cmd = [*_snakemake_base(targets, profile, pipeline), "--cores", str(cores)]
    _echo_command(cmd)
    result = subprocess.run(cmd, check=False)
    raise typer.Exit(code=result.returncode)


@app.command()
def run(
    profile: str | None = typer.Option(
        None,
        help=(
            "Snakemake profile to use. "
            "cpu: Local dev (2 cores, 2GB) | "
            "gpu: GPU workloads (1 GPU, 16GB) | "
            "slurm: HPC cluster | "
            "tee: Trusted execution with attestation. "
            "Run 'vigil doctor' to check GPU availability. "
            "See docs/profiles.md for details."
        ),
    ),
    target: list[str] = typer.Option(
        None, "--target", help="Targets to execute (defaults to all)."
    ),
    pipeline: str = typer.Option("default", help="Pipeline to operate on."),
    cores: int = typer.Option(4, min=1, help="Number of cores for execution."),
    promote_after: bool = typer.Option(
        False, "--promote", help="Promote artifacts into a receipt after execution."
    ),
) -> None:
    """Execute one or more targets and optionally promote the outputs."""
    _find_vigil_root()

    targets = _ensure_targets(target or [])
    base = _snakemake_base(targets, profile, pipeline)

    dry_cmd = [*base, "-n"]
    _echo_command(dry_cmd)
    dry_result = _run_command(dry_cmd)
    _print_output(dry_result)
    if not dry_result.ok:
        raise typer.Exit(code=dry_result.returncode)

    live_cmd = [*base, "--cores", str(cores)]
    _echo_command(live_cmd)
    live_proc = subprocess.run(live_cmd, check=False)
    if live_proc.returncode != 0:
        raise typer.Exit(code=live_proc.returncode)

    if promote_after:
        console.print("\n[bold]Running promotion...[/bold]")
        try:
            # Get vigil URL from manifest
            try:
                config, _ = vigilurl_tool.load_manifest()
                vigil_url = vigilurl_tool.build_vigil_url(config)
            except Exception:
                vigil_url = "vigil://labs.example/unknown/unknown@refs/heads/main"

            promote_tool.main(
                DEFAULT_ARTIFACTS_DIR.as_posix(),
                DEFAULT_RECEIPTS_DIR.as_posix(),
                vigil_url,
                profile,
                None,  # attestation_blob
                False,  # attest
                None,  # signing_key
            )
            _print_success(f"Promotion complete. Receipts in {DEFAULT_RECEIPTS_DIR}")
        except Exception as e:
            _print_error(f"Promotion failed: {e}")


@app.command()
def promote(
    input_dir: Path = typer.Option(DEFAULT_ARTIFACTS_DIR, "--in", help="Artifacts directory."),
    output_dir: Path = typer.Option(DEFAULT_RECEIPTS_DIR, "--out", help="Receipts directory."),
    profile: str | None = typer.Option(
        None,
        help=(
            "Profile to record in receipt. "
            "REQUIRED for tee profile: must include --attestation blob. "
            "See docs/profiles.md"
        ),
    ),
    attestation: Path | None = typer.Option(
        None,
        help=(
            "Attestation blob path (REQUIRED when using tee profile). "
            "Contains TEE hardware attestation evidence."
        ),
    ),
    attest: bool = typer.Option(
        False,
        "--attest",
        help="Generate SLSA provenance attestation alongside receipt.",
    ),
    signing_key: Path | None = typer.Option(
        None,
        "--signing-key",
        help="Path to Ed25519 private key for signing attestations (PEM format).",
    ),
) -> None:
    """Promote the latest artifacts into a signed Vigil receipt."""
    _find_vigil_root()

    try:
        # Get vigil URL from manifest
        config, _ = vigilurl_tool.load_manifest()
        vigil_url = vigilurl_tool.build_vigil_url(config)
    except Exception as e:
        _print_warning(f"Could not load vigil URL: {e}")
        vigil_url = "vigil://labs.example/unknown/unknown@refs/heads/main"

    # Validate TEE profile requirements
    if profile and profile.lower() == "tee" and not attestation:
        _print_error("TEE profile requires --attestation blob")
        console.print("\n[bold]TEE profile usage:[/bold]")
        console.print("  vigil promote --profile tee --attestation /path/to/attestation.bin")
        console.print("\n[dim]The attestation blob contains hardware-based proof of execution[/dim]")
        console.print("[dim]See docs/profiles.md for TEE profile documentation[/dim]")
        raise typer.Exit(code=1)

    if attestation and not attestation.exists():
        _print_error(f"Attestation file not found: {attestation}")
        raise typer.Exit(code=1)

    if signing_key and not signing_key.exists():
        _print_error(f"Signing key not found: {signing_key}")
        raise typer.Exit(code=1)

    try:
        with console.status("[bold green]Generating receipts..."):
            promote_tool.main(
                input_dir.as_posix(),
                output_dir.as_posix(),
                vigil_url,
                profile,
                attestation.as_posix() if attestation else None,
                attest,
                signing_key.as_posix() if signing_key else None,
            )

        panel_content = (
            f"[bold green]Receipts generated successfully[/bold green]\n\n"
            f"Output: [cyan]{output_dir}[/cyan]\n"
            f"Profile: [yellow]{profile or 'default'}[/yellow]"
        )
        if attestation:
            panel_content += f"\nTEE Attestation: [dim]{attestation}[/dim]"
        if attest:
            panel_content += "\n[bold cyan]SLSA Attestation:[/bold cyan] Generated"
        if signing_key:
            panel_content += f"\n[bold cyan]Signed with:[/bold cyan] [dim]{signing_key.name}[/dim]"

        panel = Panel(
            panel_content,
            title="✓ Promotion Complete",
            border_style="green",
        )
        console.print(panel)
    except ValueError as e:
        # Handle TEE profile validation errors from promote_tool
        if "TEE profile" in str(e):
            _print_error(str(e))
            console.print("\n[dim]Use --attestation to provide TEE attestation blob[/dim]")
            console.print("[dim]See docs/profiles.md for TEE profile documentation[/dim]")
        else:
            _print_error(f"Promotion failed: {e}")
        raise typer.Exit(code=1) from None
    except Exception as e:
        _print_error(f"Promotion failed: {e}")
        raise typer.Exit(code=1) from None


@app.command()
def verify(
    receipt: Path = typer.Argument(..., help="Path to receipt JSON file to verify."),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Print detailed verification information."
    ),
    attestation_file: Path | None = typer.Option(
        None,
        "--attestation",
        help="Path to attestation file (auto-detected if not specified).",
    ),
    signature_file: Path | None = typer.Option(
        None,
        "--signature",
        help="Path to signature file (auto-detected if not specified).",
    ),
) -> None:
    """Verify a Vigil receipt and its attestation (if present)."""
    if not receipt.exists():
        _print_error(f"Receipt not found: {receipt}")
        raise typer.Exit(code=1)

    try:
        if attestation_file:
            # Verify only the attestation
            if not attestation_file.exists():
                _print_error(f"Attestation file not found: {attestation_file}")
                raise typer.Exit(code=1)

            if verbose:
                console.print(f"\n[bold]Verifying attestation:[/bold] {attestation_file}\n")

            is_valid = verify_tool.verify_attestation(
                attestation_file, signature_file, verbose=verbose
            )
        else:
            # Verify receipt and associated attestation
            if verbose:
                console.print(f"\n[bold]Verifying receipt:[/bold] {receipt}\n")

            is_valid = verify_tool.verify_receipt_with_attestation(receipt, verbose=verbose)

        if is_valid:
            if verbose:
                console.print()
            panel = Panel(
                "[bold green]✓ Verification successful[/bold green]\n\n"
                f"Receipt: [cyan]{receipt.name}[/cyan]\n"
                "All checksums valid\n"
                "Attestation structure valid"
                + ("\nSignature verified" if signature_file or (receipt.parent / (receipt.name.replace("receipt_", "attestation_") + ".sig")).exists() else ""),
                title="✅ Verified",
                border_style="green",
            )
            console.print(panel)
        else:
            if verbose:
                console.print()
            panel = Panel(
                "[bold red]✗ Verification failed[/bold red]\n\n"
                f"Receipt: [cyan]{receipt.name}[/cyan]\n"
                "See errors above for details",
                title="❌ Failed",
                border_style="red",
            )
            console.print(panel)
            raise typer.Exit(code=1)

    except FileNotFoundError as e:
        _print_error(str(e))
        raise typer.Exit(code=1) from None
    except Exception as e:
        _print_error(f"Verification failed: {e}")
        raise typer.Exit(code=1) from None


@app.command()
def anchor(
    receipts: Path = typer.Option(
        anchor_tool.DEFAULT_RECEIPT_DIR, help="Directory containing receipts."
    ),
    record_proof: str | None = typer.Option(
        None, help="Attach a hosted proof URL to the most recent bundle."
    ),
    proof_url: str | None = typer.Option(
        None, help="Proof URL to embed during anchoring (alternative to --record-proof)."
    ),
) -> None:
    """Anchor receipts or attach a hosted proof URL to an existing bundle."""
    _find_vigil_root()

    if record_proof:
        # Use record-proof subcommand to annotate the latest bundle
        # First, find the latest bundle
        bundle_dir = anchor_tool.DEFAULT_BUNDLE_DIR
        if not bundle_dir.exists():
            _print_error("No bundles found. Run 'vigil anchor' first to create a bundle.")
            raise typer.Exit(code=1)

        bundles = sorted(bundle_dir.glob("bundle_*.json"), key=lambda p: p.name, reverse=True)
        if not bundles:
            _print_error("No bundles found. Run 'vigil anchor' first to create a bundle.")
            raise typer.Exit(code=1)

        latest_bundle = bundles[0]
        argv = [
            "record-proof",
            latest_bundle.as_posix(),
            "--proof-url",
            record_proof,
        ]

        with console.status("[bold green]Recording proof URL..."):
            exit_code = anchor_tool.main(argv)

        if exit_code == 0:
            panel = Panel(
                f"[bold green]Proof URL recorded successfully[/bold green]\n\n"
                f"Bundle: [cyan]{latest_bundle}[/cyan]\n"
                f"Proof URL: [yellow]{record_proof}[/yellow]",
                title="✓ Proof Recorded",
                border_style="green",
            )
            console.print(panel)
        raise typer.Exit(code=exit_code)
    else:
        # Build argv for anchor subcommand
        argv = ["anchor", "--receipts", receipts.as_posix()]
        if proof_url:
            argv.extend(["--proof-url", proof_url])

        with console.status("[bold green]Anchoring receipts..."):
            exit_code = anchor_tool.main(argv)

        if exit_code == 0:
            _print_success("Receipts anchored successfully")
        raise typer.Exit(code=exit_code)


@app.command()
def doctor(
    format: str = typer.Option("table", help="Output format (json or table)."),
    allow_unpinned: bool = typer.Option(
        False, "--allow-unpinned", help="Allow unpinned capsule images (for development only)"
    ),
) -> None:
    """Run repository health checks."""
    root = _find_vigil_root()

    # Run checks directly
    results = doctor_tool.perform_checks(root, allow_unpinned=allow_unpinned)
    report = doctor_tool.build_report(results)

    # Print output
    if format.lower() == "json":
        import json
        typer.echo(json.dumps(report, indent=2))
    else:
        # Use the table printer from doctor tool
        from rich.console import Console
        from rich.table import Table

        table = Table(title="Vigil Doctor Report")
        table.add_column("Code", style="bold")
        table.add_column("Status")
        table.add_column("Message", overflow="fold")
        for check in report["checks"]:
            table.add_row(check["code"], check["status"], check["message"])

        summary = report["summary"]
        footer = (
            f"Overall: {summary['status']} • "
            f"ok={summary['ok']} warning={summary['warnings']} error={summary['errors']}"
        )
        console = Console()
        console.print(table)
        console.print(footer)

    # Exit with appropriate code
    exit_code = 0 if report["summary"]["status"] != "error" else 1
    raise typer.Exit(code=exit_code)


@app.command()
def url() -> None:
    """Print the vigil:// URL for the current repository."""
    _find_vigil_root()

    try:
        config, _ = vigilurl_tool.load_manifest()
        vigil_url = vigilurl_tool.build_vigil_url(config)

        panel = Panel(
            f"[bold cyan]{vigil_url}[/bold cyan]",
            title="Vigil URL",
            border_style="cyan",
            subtitle="[dim]Use this URL to reference your project[/dim]",
        )
        console.print(panel)
    except Exception as e:
        _print_error(f"Failed to generate URL: {e}")
        raise typer.Exit(code=1) from None


@app.command()
def spec(
    sync: bool = typer.Option(False, help="Sync .vigil/workspace.spec.json with vigil.yaml"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be written without modifying files"
    ),
) -> None:
    """Manage workspace specification."""
    root = _find_vigil_root()

    if dry_run:
        try:
            spec, _ = workspace_spec_tool.sync_workspace_spec(root)
            # Output canonical JSON (sorted keys) with trailing newline
            payload = json.dumps(spec, indent=2, sort_keys=True)
            typer.echo(f"{payload}\n", nl=False)
        except Exception as e:
            _print_error(f"Failed to generate workspace spec: {e}")
            raise typer.Exit(code=1) from None
    elif sync:
        try:
            spec, target = workspace_spec_tool.sync_workspace_spec(root)
            workspace_spec_tool.write_workspace_spec(spec, target)
            _print_success(f"Updated workspace spec at {target}")
        except Exception as e:
            _print_error(f"Workspace spec sync failed: {e}")
            raise typer.Exit(code=1) from None
    else:
        console.print("[dim]Use --sync to update workspace.spec.json or --dry-run to preview.[/dim]")
        raise typer.Exit(code=0)


@app.command()
def conformance() -> None:
    """Run project-specific conformance checks (domain-specific).

    This is a domain-specific extension point that delegates to
    app/code/tools/conformance.py in your project. Different projects
    implement conformance differently based on their domain needs
    (imaging, genomics, climate, etc.).

    Example uses:
    - Compare outputs to golden baselines
    - Validate metrics against known samples
    - Check for regressions in CI/CD

    Not all projects implement this - see docs/cli-reference.md for details.
    """
    _find_vigil_root()

    cmd = ["uv", "run", "python", "-m", "app.code.tools.conformance"]
    _echo_command(cmd)
    result = subprocess.run(cmd, check=False)
    raise typer.Exit(code=result.returncode)


@ui_app.command("bootstrap")
def ui_bootstrap(
    out: Path = typer.Option(
        Path("app/code/ui/workbench_bootstrap.json"), help="Output path for Workbench JSON."
    ),
) -> None:
    """Generate Workbench bootstrap configuration for local previews."""
    _find_vigil_root()

    cmd = ["uv", "run", "python", "-m", "app.code.ui.bootstrap", "--out", out.as_posix()]
    _echo_command(cmd)
    result = subprocess.run(cmd, check=False)
    raise typer.Exit(code=result.returncode)


@mcp_app.command("serve")
def mcp_serve() -> None:
    """Start the MCP server exposing preview_data, run_target, and promote."""
    _find_vigil_root()

    # Check if MCP dependencies are installed
    try:
        import mcp  # type: ignore[import-not-found]  # noqa: F401
        import polars  # type: ignore[import-not-found]  # noqa: F401
    except ImportError:
        _print_error(
            "MCP server dependencies not installed. "
            "Install them with: uv tool install 'vigil[mcp]'"
        )
        console.print("\n[bold]The MCP server requires optional dependencies:[/bold]")
        console.print("  • mcp>=1.1.0")
        console.print("  • polars>=0.20.0")
        console.print("\n[bold cyan]To install:[/bold cyan]")
        console.print("  uv tool install 'vigil[mcp]'")
        console.print("  [dim]or[/dim]")
        console.print("  pip install 'vigil[mcp]'")
        raise typer.Exit(code=1) from None

    cmd = ["uv", "run", "python", "-m", "vigil.mcp"]
    _echo_command(cmd)
    result = subprocess.run(cmd, check=False)
    raise typer.Exit(code=result.returncode)


@ai_app.command("propose")
def ai_propose(
    cores: int = typer.Option(4, min=1, help="Number of cores requested for execution."),
) -> None:
    """Generate a Suggestion Cell and record a dry-run state for auto-target."""
    _find_vigil_root()

    cmd = ["uv", "run", "python", "-m", "app.code.ai.auto_target", "propose", "--cores", str(cores)]
    _echo_command(cmd)
    result = subprocess.run(cmd, check=False)
    raise typer.Exit(code=result.returncode)


@ai_app.command("apply")
def ai_apply(
    skip_promote: bool = typer.Option(False, help="Skip promotion after executing targets."),
) -> None:
    """Execute the targets recorded during propose and optionally promote outputs."""
    _find_vigil_root()

    cmd = ["uv", "run", "python", "-m", "app.code.ai.auto_target", "apply"]
    if skip_promote:
        cmd.append("--skip-promote")
    _echo_command(cmd)
    result = subprocess.run(cmd, check=False)
    raise typer.Exit(code=result.returncode)


@notes_app.command("new")
def notes_new(
    note_type: str = typer.Argument(..., help="Type of note: 'experiment' or 'protocol'"),
    title: str = typer.Argument(..., help="Title of the note"),
    author: str = typer.Option(..., help="Author name"),
    status: str = typer.Option(
        "in_progress",
        help="Experiment status (in_progress, completed, failed) - for experiments only",
    ),
    tags: str = typer.Option("", help="Comma-separated tags - for experiments only"),
    version: str = typer.Option("1.0", help="Protocol version - for protocols only"),
) -> None:
    """Create a new lab notebook entry from a template."""
    from vigil.notes import create_experiment_entry, create_protocol

    root = _find_vigil_root()

    # Normalize note type
    note_type = note_type.lower()
    if note_type not in ["experiment", "protocol"]:
        _print_error(f"Unknown note type: {note_type}. Use 'experiment' or 'protocol'.")
        raise typer.Exit(code=1)

    try:
        if note_type == "experiment":
            # Create experiment entry
            experiments_dir = root / "app" / "notes" / "experiments"
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

            output_path = create_experiment_entry(
                title=title,
                author=author,
                output_dir=experiments_dir,
                status=status,
                tags=tag_list,
            )

            panel = Panel(
                f"[bold green]Experiment entry created[/bold green]\n\n"
                f"Title: [cyan]{title}[/cyan]\n"
                f"Author: [yellow]{author}[/yellow]\n"
                f"Status: [dim]{status}[/dim]\n"
                f"File: [dim]{output_path.relative_to(root)}[/dim]",
                title="Experiment Created",
                border_style="green",
            )
            console.print(panel)

        else:  # protocol
            # Create protocol
            protocols_dir = root / "app" / "notes" / "protocols"

            output_path = create_protocol(
                title=title,
                author=author,
                output_dir=protocols_dir,
                version=version,
            )

            panel = Panel(
                f"[bold green]Protocol created[/bold green]\n\n"
                f"Title: [cyan]{title}[/cyan]\n"
                f"Author: [yellow]{author}[/yellow]\n"
                f"Version: [dim]{version}[/dim]\n"
                f"File: [dim]{output_path.relative_to(root)}[/dim]",
                title="Protocol Created",
                border_style="green",
            )
            console.print(panel)

        # Remind user to regenerate index
        console.print("\n[dim]Run 'vigil notes index' to update the lab notebook index.[/dim]")

    except Exception as e:
        _print_error(f"Failed to create {note_type}: {e}")
        raise typer.Exit(code=1) from None


@notes_app.command("index")
def notes_index() -> None:
    """Regenerate the lab notebook index (README.md)."""
    from vigil.notes import generate_index

    root = _find_vigil_root()
    notes_dir = root / "app" / "notes"

    if not notes_dir.exists():
        _print_error("app/notes/ directory not found. Create notes first with 'vigil notes new'.")
        raise typer.Exit(code=1)

    try:
        with console.status("[bold green]Generating index..."):
            index_path = generate_index(notes_dir)

        # Count entries
        experiments_dir = notes_dir / "experiments"
        protocols_dir = notes_dir / "protocols"

        num_experiments = len(list(experiments_dir.glob("*.md"))) if experiments_dir.exists() else 0
        num_protocols = (
            len([p for p in protocols_dir.glob("*.md") if p.name.lower() != "readme.md"])
            if protocols_dir.exists()
            else 0
        )

        panel = Panel(
            f"[bold green]Index regenerated[/bold green]\n\n"
            f"Experiments: [cyan]{num_experiments}[/cyan]\n"
            f"Protocols: [cyan]{num_protocols}[/cyan]\n"
            f"Index: [dim]{index_path.relative_to(root)}[/dim]",
            title="Index Updated",
            border_style="green",
        )
        console.print(panel)

    except Exception as e:
        _print_error(f"Failed to generate index: {e}")
        raise typer.Exit(code=1) from None


@card_app.command("lint")
def card_lint(
    path: Path = typer.Argument(..., help="Path to the card file (README.md)"),
    card_type: str | None = typer.Option(
        None,
        "--type",
        help="Card type: 'experiment' or 'dataset'. Auto-detected if not specified.",
    ),
) -> None:
    """Lint a card file against schema requirements."""
    from vigil.cards.linter import lint_card

    if not path.exists():
        _print_error(f"File not found: {path}")
        raise typer.Exit(code=1)

    # Lint the card
    result = lint_card(path, card_type)

    # Display results
    if result.valid:
        _print_success(f"Card is valid: {path}")
    else:
        _print_error(f"Card validation failed: {path}")

    # Show errors
    if result.errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for error in result.errors:
            console.print(f"  [red]✗[/red] {error}")

    # Show warnings
    if result.warnings:
        console.print("\n[bold yellow]Warnings:[/bold yellow]")
        for warning in result.warnings:
            console.print(f"  [yellow]⚠[/yellow] {warning}")

    # Exit with appropriate code
    if not result.valid:
        raise typer.Exit(code=1)


@card_app.command("init")
def card_init(
    card_type: str = typer.Argument(
        ..., help="Type of card to create: 'experiment' or 'dataset'"
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Output path (defaults to README.md or app/data/README.md)"
    ),
) -> None:
    """Create a new card from template."""
    import shutil

    import vigil

    # Validate card type
    if card_type not in ["experiment", "dataset"]:
        _print_error(f"Unknown card type: {card_type}. Use 'experiment' or 'dataset'")
        raise typer.Exit(code=1)

    # Determine output path
    if output is None:
        if card_type == "experiment":
            output = Path("README.md")
        else:  # dataset
            output = Path("app/data/README.md")

    # Check if file already exists
    if output.exists():
        _print_error(f"File already exists: {output}")
        console.print("[dim]Use a different --output path or remove the existing file[/dim]")
        raise typer.Exit(code=1)

    # Find template
    vigil_path = Path(vigil.__file__).parent
    template_name = f"{card_type}_card.md"
    template_path = vigil_path / "cards" / "templates" / template_name

    if not template_path.exists():
        _print_error(f"Template not found: {template_path}")
        raise typer.Exit(code=1)

    # Create output directory if needed
    output.parent.mkdir(parents=True, exist_ok=True)

    # Copy template
    try:
        shutil.copy(template_path, output)
        _print_success(f"Created {card_type} card: {output}")
        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"  1. Edit the card: [cyan]{output}[/cyan]")
        console.print(f"  2. Validate the card: [cyan]vigil card lint {output}[/cyan]")
    except Exception as e:
        _print_error(f"Failed to create card: {e}")
        raise typer.Exit(code=1) from None


def main() -> None:
    """Entrypoint for the vigil CLI."""
    app()


if __name__ == "__main__":
    main()
