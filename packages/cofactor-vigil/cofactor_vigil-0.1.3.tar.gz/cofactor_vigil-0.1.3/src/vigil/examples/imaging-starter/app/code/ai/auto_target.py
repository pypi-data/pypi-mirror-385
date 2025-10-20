"""Auto-Target agent coordinating Snakemake runs through the MCP server."""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

from mcp.types import CallToolResult, TextContent

from app.code.ai import assistant
from app.code.ai.mcp import server as mcp_server

DEFAULT_SUGGESTION_PATH = Path("app/code/ai/suggestions/auto_target.py")
DEFAULT_STATE_PATH = Path("app/code/ai/auto_target_state.json")
DEFAULT_REPORT_PATH = Path("AUTO_TARGET_REPORT.md")
DEFAULT_RECEIPT_LOG = Path("app/code/ai/auto_target_receipt.json")
DEFAULT_ARTIFACTS_DIR = Path("app/code/artifacts")
DEFAULT_RECEIPTS_DIR = Path("app/code/receipts")
DEFAULT_VIGIL_URL = "vigil://labs.example/your-org/your-project@refs/heads/main"


def _now() -> str:
    return datetime.now(tz=UTC).isoformat()


def _extract_text(result: CallToolResult) -> str:
    chunks: list[str] = []
    for item in result.content:
        if isinstance(item, TextContent):
            chunks.append(item.text)
    return "\n\n".join(chunk for chunk in chunks if chunk.strip())


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


@dataclass(slots=True)
class AutoTargetState:
    """Serialized state persisted between dry-run and execution."""

    targets: list[str]
    profile: str | None
    cores: int
    suggestion_path: str
    dry_run_ok: bool
    dry_run_message: str
    created_at: str
    last_updated_at: str
    run_message: str | None = None
    promoted: bool = False
    metrics_path: str | None = None
    metrics: dict[str, Any] | None = field(default=None)
    receipt_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> AutoTargetState:
        return cls(
            targets=list(payload.get("targets", [])),
            profile=payload.get("profile"),
            cores=int(payload.get("cores", 4)),
            suggestion_path=str(payload.get("suggestion_path", "")),
            dry_run_ok=bool(payload.get("dry_run_ok", False)),
            dry_run_message=str(payload.get("dry_run_message", "")),
            created_at=str(payload.get("created_at", _now())),
            last_updated_at=str(payload.get("last_updated_at", _now())),
            run_message=payload.get("run_message"),
            promoted=bool(payload.get("promoted", False)),
            metrics_path=payload.get("metrics_path"),
            metrics=payload.get("metrics"),
            receipt_path=payload.get("receipt_path"),
        )


class ActionReceiptLogger:
    """Append-only log capturing Auto-Target decisions."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, entry: dict[str, Any]) -> None:
        record = {"events": []}
        if self.path.exists():
            try:
                record = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                record = {"events": []}
        record.setdefault("events", []).append(entry)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(record, indent=2), encoding="utf-8")


class AutoTargetAgent:
    """Coordinates dry-run, execution, and promotion through MCP verbs."""

    def __init__(
        self,
        suggestion_path: Path = DEFAULT_SUGGESTION_PATH,
        state_path: Path = DEFAULT_STATE_PATH,
        report_path: Path = DEFAULT_REPORT_PATH,
        receipt_log_path: Path = DEFAULT_RECEIPT_LOG,
        artifacts_dir: Path = DEFAULT_ARTIFACTS_DIR,
        receipts_dir: Path = DEFAULT_RECEIPTS_DIR,
        vigil_url: str = DEFAULT_VIGIL_URL,
    ) -> None:
        self.suggestion_path = suggestion_path
        self.state_path = state_path
        self.report_path = report_path
        self.logger = ActionReceiptLogger(receipt_log_path)
        self.artifacts_dir = artifacts_dir
        self.receipts_dir = receipts_dir
        self.vigil_url = vigil_url

    def _write_state(self, state: AutoTargetState) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")

    def _read_state(self) -> AutoTargetState:
        if not self.state_path.exists():
            raise FileNotFoundError("Auto-Target state not found; run propose first")
        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Auto-Target state file is corrupted") from exc
        return AutoTargetState.from_dict(payload)

    def _log(self, action: str, **details: Any) -> None:
        entry = {"action": action, "timestamp": _now(), **details}
        self.logger.append(entry)

    def _render_targets(self, panel_state: dict[str, Any]) -> list[str]:
        rendered = assistant._render_targets(panel_state)  # type: ignore[attr-defined]
        return rendered

    def _build_arguments(
        self,
        targets: list[str],
        profile: str | None,
        cores: int,
        promote: bool,
    ) -> dict[str, Any]:
        args: dict[str, Any] = {
            "targets": targets,
            "cores": cores,
            "promote": promote,
            "promotion_input_dir": str(self.artifacts_dir),
            "promotion_output_dir": str(self.receipts_dir),
            "promotion_vigil_url": self.vigil_url,
        }
        if profile:
            args["profile"] = profile
        if promote:
            args["promote_confirm"] = True
        return args

    def propose(self, panel_state: dict[str, Any], cores: int = 4) -> AutoTargetState:
        """Generate a Suggestion Cell and record a dry-run via run_target."""

        targets = self._render_targets(panel_state)
        profile = panel_state.get("profile") if isinstance(panel_state, dict) else None
        suggestion = assistant.suggest_cell(panel_state)
        self.suggestion_path.parent.mkdir(parents=True, exist_ok=True)
        self.suggestion_path.write_text(suggestion, encoding="utf-8")

        call_args = self._build_arguments(targets, profile, cores, promote=False)
        dry_result = asyncio.run(mcp_server.call_tool("run_target", call_args))
        dry_message = _extract_text(dry_result)
        dry_ok = "failed" not in dry_message.lower()

        state = AutoTargetState(
            targets=targets,
            profile=profile if isinstance(profile, str) else None,
            cores=cores,
            suggestion_path=str(self.suggestion_path),
            dry_run_ok=dry_ok,
            dry_run_message=dry_message,
            created_at=_now(),
            last_updated_at=_now(),
        )
        self._write_state(state)
        self._log("propose", targets=targets, profile=profile, dry_run_ok=dry_ok)
        return state

    def _load_metrics(self) -> tuple[str | None, dict[str, Any] | None]:
        metrics_path = self.artifacts_dir / "metrics.json"
        metrics = _load_json(metrics_path)
        if not metrics:
            return None, None
        return metrics_path.as_posix(), metrics

    def _discover_receipt(self) -> str | None:
        if not self.receipts_dir.exists():
            return None
        receipts = sorted(self.receipts_dir.glob("receipt_*.json"))
        if not receipts:
            return None
        return receipts[-1].as_posix()

    def _render_report(self, metrics: dict[str, Any] | None, receipt_path: str | None) -> str:
        lines = ["# Auto-Target Report", ""]
        if metrics:
            lines.append("## Metrics snapshot")
            lines.append("| metric | value |")
            lines.append("| --- | --- |")
            for key in ("n", "accuracy", "precision", "recall", "f1"):
                if key in metrics:
                    lines.append(f"| {key} | {metrics[key]} |")
            lines.append("")
        else:
            lines.append("## Metrics snapshot")
            lines.append("No metrics were discovered after execution.")
            lines.append("")

        lines.append("## Receipt")
        if receipt_path:
            lines.append(f"Latest receipt: `{receipt_path}`")
        else:
            lines.append("No receipt detected; ensure promote.py completed successfully.")
        lines.append("")
        return "\n".join(lines)

    def apply(self, auto_promote: bool = True) -> AutoTargetState:
        """Run the approved targets, promote outputs, and update the PR report."""

        state = self._read_state()
        if not state.dry_run_ok:
            raise RuntimeError("Dry-run did not succeed; resolve issues before apply")

        call_args = self._build_arguments(state.targets, state.profile, state.cores, promote=auto_promote)
        call_args["confirm"] = True

        run_result = asyncio.run(mcp_server.call_tool("run_target", call_args))
        run_message = _extract_text(run_result)

        metrics_path, metrics = self._load_metrics()
        receipt_path = self._discover_receipt() if auto_promote else None

        report = self._render_report(metrics, receipt_path)
        self.report_path.write_text(report, encoding="utf-8")

        updated_state = AutoTargetState(
            targets=state.targets,
            profile=state.profile,
            cores=state.cores,
            suggestion_path=state.suggestion_path,
            dry_run_ok=state.dry_run_ok,
            dry_run_message=state.dry_run_message,
            created_at=state.created_at,
            last_updated_at=_now(),
            run_message=run_message,
            promoted=auto_promote,
            metrics_path=metrics_path,
            metrics=metrics,
            receipt_path=receipt_path,
        )

        self._write_state(updated_state)
        self._log(
            "apply",
            run_ok="execution failed" not in run_message.lower(),
            promoted=auto_promote,
            metrics_path=metrics_path,
            receipt_path=receipt_path,
        )
        return updated_state


def _load_panel_state(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return _load_json(path)


def _parse_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--suggestion-path", type=Path, default=DEFAULT_SUGGESTION_PATH)
    parser.add_argument("--state-path", type=Path, default=DEFAULT_STATE_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--receipt-log", type=Path, default=DEFAULT_RECEIPT_LOG)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS_DIR)
    parser.add_argument("--receipts-dir", type=Path, default=DEFAULT_RECEIPTS_DIR)
    parser.add_argument("--vigil-url", default=DEFAULT_VIGIL_URL)


def _build_agent_from_args(args: argparse.Namespace) -> AutoTargetAgent:
    return AutoTargetAgent(
        suggestion_path=args.suggestion_path,
        state_path=args.state_path,
        report_path=args.report_path,
        receipt_log_path=args.receipt_log,
        artifacts_dir=args.artifacts_dir,
        receipts_dir=args.receipts_dir,
        vigil_url=args.vigil_url,
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    propose_parser = subparsers.add_parser("propose", help="Generate suggestion + dry-run")
    _parse_common_args(propose_parser)
    propose_parser.add_argument("--panel-state", type=Path, help="JSON file with Vigil panel state")
    propose_parser.add_argument("--cores", type=int, default=4)

    apply_parser = subparsers.add_parser("apply", help="Execute approved targets and promote")
    _parse_common_args(apply_parser)
    apply_parser.add_argument("--skip-promote", action="store_true")

    args = parser.parse_args(argv)
    agent = _build_agent_from_args(args)

    if args.command == "propose":
        panel_state = _load_panel_state(getattr(args, "panel_state", None))
        state = agent.propose(panel_state, cores=args.cores)
        print(json.dumps(state.to_dict(), indent=2))
        return

    if args.command == "apply":
        state = agent.apply(auto_promote=not args.skip_promote)
        print(json.dumps(state.to_dict(), indent=2))
        return


if __name__ == "__main__":
    main()
