from __future__ import annotations

import argparse
from pathlib import Path

from vigil.tools import vigilurl

OPEN_LINK_MARKER = "<!-- vigil-open-link -->"
METRICS_MARKER = "<!-- vigil-metrics-comment -->"


def _build_vigil_url_with_ref(ref: str | None) -> str:
    cfg, _ = vigilurl.load_manifest()
    base_url = vigilurl.build_vigil_url(cfg)
    if ref:
        return f"{base_url}&ref={ref}"
    return base_url


def render_vigil_link_comment(ref: str | None) -> str:
    url = _build_vigil_url_with_ref(ref)
    body_lines = [
        "🔗 **Open in Vigil**",
        "",
        url,
        "",
        "Exact ref, pinned capsule, short-lived creds → **Receipt**.",
        "",
        OPEN_LINK_MARKER,
    ]
    return "\n".join(body_lines)


def render_metrics_comment(
    table_text: str,
    *,
    receipt_url: str | None = None,
    receipt_name: str | None = None,
    receipt_path: str | None = None,
    anchor_text: str | None = None,
) -> str:
    table = table_text.strip()

    receipt_text = "none generated"
    if receipt_url:
        label = f"Download {receipt_name}" if receipt_name else "Download latest receipt"
        receipt_text = f"[{label}]({receipt_url})"
    elif receipt_path:
        receipt_text = f"`{receipt_path}`"

    anchor_value = anchor_text or "pending anchor proof"

    body_lines = [
        "## 📊 Metrics & Receipt",
        "",
        table,
        "",
        f"**Receipt:** {receipt_text}",
        f"**Anchor Proof:** {anchor_value}",
        "",
        "🔍 Evidence generated from the latest Vigil run.",
        METRICS_MARKER,
    ]
    return "\n".join(body_lines)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render GitHub PR comments for Vigil workflows.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    link_parser = subparsers.add_parser("link", help="Render the Vigil link comment")
    link_parser.add_argument("--ref", help="Git reference (commit SHA)", required=False)

    metrics_parser = subparsers.add_parser("metrics", help="Render the metrics summary comment")
    metrics_parser.add_argument("--table", required=True, help="Path to the markdown metrics table")
    metrics_parser.add_argument("--receipt-url", help="Public URL for downloading the receipt")
    metrics_parser.add_argument("--receipt-name", help="Name of the uploaded receipt artifact")
    metrics_parser.add_argument("--receipt-path", help="Local path to the receipt file")
    metrics_parser.add_argument("--anchor-text", help="Anchor proof description or link")

    return parser.parse_args()


def _cmd_link(args: argparse.Namespace) -> int:
    body = render_vigil_link_comment(args.ref)
    print(body)
    return 0


def _cmd_metrics(args: argparse.Namespace) -> int:
    table_path = Path(args.table)
    table_text = table_path.read_text(encoding="utf-8")
    body = render_metrics_comment(
        table_text,
        receipt_url=args.receipt_url,
        receipt_name=args.receipt_name,
        receipt_path=args.receipt_path,
        anchor_text=args.anchor_text,
    )
    print(body)
    return 0


def main() -> int:
    args = _parse_args()
    if args.command == "link":
        return _cmd_link(args)
    if args.command == "metrics":
        return _cmd_metrics(args)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
