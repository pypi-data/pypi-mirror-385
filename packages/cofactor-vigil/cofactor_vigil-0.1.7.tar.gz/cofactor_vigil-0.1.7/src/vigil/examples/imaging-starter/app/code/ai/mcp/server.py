"""MCP server exposing scientific workflow verbs to external assistants."""

from __future__ import annotations

import asyncio
import json
import shlex
import subprocess
import time
from collections import deque
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import polars as pl
import yaml
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, TextContent, Tool

from ...lib.paths import PROJECT_ROOT, ensure_project_on_path, project_path

ensure_project_on_path()

if TYPE_CHECKING:
    from collections.abc import Callable

SPEC_PATH = Path(__file__).parent.parent / "toolspec.yaml"
PREVIEW_RATE_LIMIT = 3
PREVIEW_RATE_WINDOW_SECONDS = 60.0
PREVIEW_MAX_ROWS = 200
PROMOTION_DEFAULT_VIGIL_URL = "vigil://labs.example/your-org/your-project@refs/heads/main"


@dataclass(slots=True)
class _RateLimiter:
    """Simple sliding-window rate limiter for preview_data requests."""

    max_calls: int
    window_seconds: float
    timestamps: deque[float]

    @classmethod
    def create(cls, max_calls: int, window_seconds: float) -> _RateLimiter:
        return cls(max_calls=max_calls, window_seconds=window_seconds, timestamps=deque())

    def _prune(self, now: float) -> None:
        while self.timestamps and now - self.timestamps[0] >= self.window_seconds:
            self.timestamps.popleft()

    def allow(self) -> tuple[bool, float]:
        now = time.monotonic()
        self._prune(now)
        if len(self.timestamps) >= self.max_calls:
            retry_after = self.window_seconds - (now - self.timestamps[0])
            return False, max(0.0, retry_after)
        self.timestamps.append(now)
        return True, 0.0

    def reset(self) -> None:
        self.timestamps.clear()


_preview_rate_limiter = _RateLimiter.create(
    max_calls=PREVIEW_RATE_LIMIT,
    window_seconds=PREVIEW_RATE_WINDOW_SECONDS,
)


def _load_toolspec() -> dict[str, Any]:
    try:
        return yaml.safe_load(SPEC_PATH.read_text(encoding="utf-8")) or {}
    except FileNotFoundError:
        raise RuntimeError(f"toolspec not found at {SPEC_PATH}") from None


SPEC_DATA = _load_toolspec()
VERB_ENTRIES: list[dict[str, Any]] = [v for v in SPEC_DATA.get("verbs", []) if isinstance(v, dict)]
ALLOWED_VERBS = {entry["name"] for entry in VERB_ENTRIES if "name" in entry}


@dataclass(slots=True)
class CommandResult:
    ok: bool
    stdout: str
    stderr: str

    def merged_output(self) -> str:
        text = "\n".join(part for part in (self.stdout.strip(), self.stderr.strip()) if part)
        return text.strip() or "(no output)"


def run_command(cmd: Sequence[str]) -> CommandResult:
    """Run a command without raising, returning stdout/stderr."""

    proc = subprocess.run(
        list(cmd),
        capture_output=True,
        text=True,
        check=False,
        cwd=str(PROJECT_ROOT),
    )
    return CommandResult(proc.returncode == 0, proc.stdout, proc.stderr)


def _render_targets(arguments: dict[str, Any]) -> list[str]:
    if "targets" in arguments and arguments["targets"] is not None:
        raw = arguments["targets"]
        if isinstance(raw, str):
            return shlex.split(raw)
        if isinstance(raw, Iterable):
            return [str(item) for item in raw]

    single = arguments.get("target", "all")
    if isinstance(single, str):
        return shlex.split(single)
    return ["all"]


def _snakemake_base(targets: list[str], profile: str | None) -> list[str]:
    base = ["uv", "run", "snakemake", "-s", "app/code/pipelines/Snakefile"]
    base.extend(targets)
    if profile:
        base.extend(["--profile", profile])
    return base


def _build_run_target_tool() -> Tool:
    return Tool(
        name="run_target",
        description="Dry-run, execute, and optionally promote a Snakemake target",
        inputSchema={
            "type": "object",
            "properties": {
                "targets": {
                    "type": ["array", "string"],
                    "items": {"type": "string"},
                    "description": "Explicit targets to operate on (defaults to 'all')",
                },
                "target": {
                    "type": "string",
                    "description": "Pipeline target to run (e.g., 'all', 'processed.parquet')",
                },
                "profile": {
                    "type": "string",
                    "description": "Optional Snakemake profile to use",
                },
                "cores": {
                    "type": "integer",
                    "description": "Number of cores for execution phase",
                    "default": 4,
                    "minimum": 1,
                },
                "confirm": {
                    "type": "boolean",
                    "description": "Set true to execute after dry-run",
                    "default": False,
                },
                "promote": {
                    "type": "boolean",
                    "description": "Set true to trigger promote.py after execution succeeds",
                    "default": False,
                },
                "promote_confirm": {
                    "type": "boolean",
                    "description": "Second confirmation required when promote=true",
                    "default": False,
                },
                "promotion_output_dir": {
                    "type": "string",
                    "description": "Receipt output directory for promotion step",
                    "default": "app/code/receipts",
                },
                "promotion_input_dir": {
                    "type": "string",
                    "description": "Artifact directory provided to promote.py",
                    "default": "app/code/artifacts",
                },
                "promotion_vigil_url": {
                    "type": "string",
                    "description": "Vigil URL recorded in generated receipts",
                    "default": "vigil://labs.example/your-org/your-project@refs/heads/main",
                },
            },
            "required": [],
        },
    )


def _build_promote_tool() -> Tool:
    return Tool(
        name="promote",
        description="Generate receipts for completed runs",
        inputSchema={
            "type": "object",
            "properties": {
                "confirm": {
                    "type": "boolean",
                    "description": "Set true to actually generate receipts",
                    "default": False,
                },
                "input_dir": {
                    "type": "string",
                    "description": "Input directory containing artifacts",
                    "default": "app/code/artifacts",
                },
                "output_dir": {
                    "type": "string",
                    "description": "Output directory for receipts",
                    "default": "app/code/receipts",
                },
                "vigil_url": {
                    "type": "string",
                    "description": "Vigil URL to record in the receipt",
                    "default": "vigil://labs.example/your-org/your-project@refs/heads/main",
                },
            },
        },
    )


def _build_preview_tool() -> Tool:
    return Tool(
        name="preview_data",
        description="Inspect a data handle and return a row sample",
        inputSchema={
            "type": "object",
            "properties": {
                "handle_path": {
                    "type": "string",
                    "description": "Path to data handle JSON file",
                    "default": "app/data/handles/data.parquet.dhandle.json",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of rows to preview",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 500,
                },
            },
        },
    )


_TOOL_BUILDERS: dict[str, Callable[[], Tool]] = {
    "run_target": _build_run_target_tool,
    "promote": _build_promote_tool,
    "preview_data": _build_preview_tool,
}

unknown_verbs = ALLOWED_VERBS - _TOOL_BUILDERS.keys()
if unknown_verbs:
    raise RuntimeError(f"toolspec declares unsupported verbs: {', '.join(sorted(unknown_verbs))}")


app = Server("scientific-workflow")


def _declared_tools() -> list[Tool]:
    tools: list[Tool] = []
    for entry in VERB_ENTRIES:
        name = entry.get("name")
        if isinstance(name, str):
            builder = _TOOL_BUILDERS.get(name)
            if builder:
                tools.append(builder())
    return tools


def _clamp_preview_limit(limit: int) -> int:
    return max(1, min(limit, PREVIEW_MAX_ROWS))


def _load_handle_rows(handle_path: str | Path, requested_limit: int) -> str:
    try:
        handle_file = project_path(handle_path)
        handle = json.loads(handle_file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return f"Handle not found: {handle_path}"
    except json.JSONDecodeError as exc:
        return f"Invalid handle JSON: {exc}"

    clamped_limit = _clamp_preview_limit(requested_limit)
    effective_limit = clamped_limit
    redact_cols = set(handle.get("redact_columns", []))
    offline = handle.get("offline_fallback")
    try:
        if offline:
            frame = pl.read_csv(project_path(offline), n_rows=clamped_limit)
        else:
            uri = handle.get("uri")
            guidance = (
                "Handle is missing an 'offline_fallback'. Add a small sample under "
                "app/data/samples/ and set offline_fallback to that path so previews "
                "work without remote storage access."
            )
            if not uri:
                return f"{guidance} The handle also lacks a 'uri' for online preview."
            return (
                f"{guidance} Online preview would require accessing the remote URI: {uri}"
            )
    except FileNotFoundError:
        return "Data source not found for preview"
    except Exception as exc:  # noqa: BLE001 - surface underlying issue
        return f"Error loading data: {exc}"

    if redact_cols:
        frame = frame.drop([col for col in redact_cols if col in frame.columns])

    rows = frame.head(clamped_limit).to_dicts()
    payload = {
        "columns": frame.columns,
        "requested_limit": requested_limit,
        "limit": clamped_limit,
        "max_rows": PREVIEW_MAX_ROWS,
        "effective_limit": effective_limit,
        "returned": len(rows),
        "rows": rows,
    }
    return json.dumps(payload, indent=2)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools defined by the toolspec."""
    return _declared_tools()


async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    """Execute a tool declared in the toolspec."""
    if name not in ALLOWED_VERBS:
        return CallToolResult(content=[TextContent(type="text", text=f"tool '{name}' not allowed")])

    if name == "run_target":
        targets = _render_targets(arguments)
        profile = arguments.get("profile")
        base_args = _snakemake_base(targets, profile)

        dry_result = run_command([*base_args, "-n"])
        dry_output = dry_result.merged_output()
        target_label = " ".join(targets) or "all"

        if not dry_result.ok:
            message = (
                f"Dry-run for target(s) '{target_label}' failed:\n{dry_output}\n\n"
                "No execution attempted. Resolve the dry-run errors before confirming."
            )
            return CallToolResult(content=[TextContent(type="text", text=message)])

        if not arguments.get("confirm", False):
            message = (
                f"Dry-run for target(s) '{target_label}':\n{dry_output}\n\n"
                "No changes executed. Re-run with confirm=true to apply."
            )
            if arguments.get("promote"):
                message += (
                    "\nPromotion requested but requires confirm=true and promote_confirm=true "
                    "on a follow-up call."
                )
            return CallToolResult(content=[TextContent(type="text", text=message)])

        cores = int(arguments.get("cores", 4) or 4)
        live_args = [*base_args, "--cores", str(max(1, cores))]
        live_result = run_command(live_args)
        live_output = live_result.merged_output()

        if not live_result.ok:
            combined = (
                f"Dry-run output:\n{dry_output}\n\n"
                f"Execution failed:\n{live_output}"
            )
            return CallToolResult(content=[TextContent(type="text", text=combined)])

        sections = [
            f"Dry-run output:\n{dry_output}",
            f"Execution output:\n{live_output}",
        ]

        if arguments.get("promote"):
            if not arguments.get("promote_confirm", False):
                sections.append(
                    "Promotion was requested. Re-run with promote_confirm=true to invoke promote.py "
                    "after a successful execution."
                )
                return CallToolResult(
                    content=[TextContent(type="text", text="\n\n".join(sections))]
                )

            promote_cmd = [
                "uv",
                "run",
                "python",
                str(project_path("app/code/tools/promote.py")),
                "--in",
                str(project_path(arguments.get("promotion_input_dir", "app/code/artifacts"))),
                "--out",
                str(project_path(arguments.get("promotion_output_dir", "app/code/receipts"))),
                "--vigil-url",
                str(arguments.get("promotion_vigil_url", PROMOTION_DEFAULT_VIGIL_URL)),
            ]
            promote_result = run_command(promote_cmd)
            promote_output = promote_result.merged_output()
            if not promote_result.ok:
                sections.append(f"Promotion failed:\n{promote_output}")
            else:
                sections.append(f"Promotion output:\n{promote_output}")

        return CallToolResult(content=[TextContent(type="text", text="\n\n".join(sections))])

    if name == "promote":
        if not arguments.get("confirm", False):
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=(
                            "Promotion requires explicit confirmation. "
                            "Re-run with confirm=true after verifying outputs."
                        ),
                    )
                ]
            )
        input_dir = project_path(arguments.get("input_dir", "app/code/artifacts"))
        output_dir = project_path(arguments.get("output_dir", "app/code/receipts"))
        promote_cmd = [
            "uv",
            "run",
            "python",
            str(project_path("app/code/tools/promote.py")),
            "--in",
            str(input_dir),
            "--out",
            str(output_dir),
            "--vigil-url",
            str(arguments.get("vigil_url", PROMOTION_DEFAULT_VIGIL_URL)),
        ]
        result = run_command(promote_cmd)
        message = (
            "Promotion succeeded:\n" + result.merged_output()
            if result.ok
            else "Promotion failed:\n" + result.merged_output()
        )
        return CallToolResult(content=[TextContent(type="text", text=message)])

    if name == "preview_data":
        allowed, retry_after = _preview_rate_limiter.allow()
        if not allowed:
            wait_seconds = int(retry_after) + 1
            message = (
                "preview_data rate limit exceeded. "
                f"Try again in approximately {wait_seconds} second(s)."
            )
            return CallToolResult(content=[TextContent(type="text", text=message)])
        handle_path = arguments.get("handle_path", "app/data/handles/data.parquet.dhandle.json")
        try:
            requested_limit = int(arguments.get("limit", 100))
        except (TypeError, ValueError):
            requested_limit = 100
        preview = _load_handle_rows(handle_path, requested_limit)
        return CallToolResult(content=[TextContent(type="text", text=preview)])

    # Should not be reachable thanks to ALLOWED_VERBS check
    return CallToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])


@app.call_tool()
async def _call_tool_handler(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Adapter that returns raw content blocks for the MCP transport."""

    result = await call_tool(name, arguments)
    return list(result.content)


async def main() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="scientific-workflow",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
