"""Data panel that previews table handles for the Vigil Workbench."""

from __future__ import annotations

import json
from collections.abc import Iterable  # noqa: TCH003
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import duckdb
import pyarrow as pa  # noqa: TCH002

from app.code.lib.paths import project_path

DEFAULT_HANDLES_DIR = project_path("app/data/handles")
DEFAULT_SAMPLE_SIZE = 20


@dataclass(slots=True)
class TablePreview:
    """Container holding sampled table data and schema metadata."""

    name: str
    handle_path: Path
    schema: list[dict[str, str]]
    rows: list[dict[str, Any]]
    metadata: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation expected by the Workbench."""

        return {
            "name": self.name,
            "handlePath": str(self.handle_path),
            "schema": self.schema,
            "rows": self.rows,
            "metadata": self.metadata,
        }


def build_panel(
    *, handles_dir: Path | None = None, sample_size: int = DEFAULT_SAMPLE_SIZE
) -> dict[str, Any]:
    """Return the Workbench configuration for the data explorer panel."""

    previews = list(
        load_table_previews(handles_dir=handles_dir, sample_size=sample_size)
    )
    return {
        "id": "data-panel",
        "label": "Data Handles",
        "type": "tableBrowser",
        "tables": [preview.as_dict() for preview in previews],
    }


def load_table_previews(
    *, handles_dir: Path | None = None, sample_size: int = DEFAULT_SAMPLE_SIZE
) -> Iterable[TablePreview]:
    """Yield ``TablePreview`` instances for each data handle on disk."""

    directory = project_path(handles_dir) if handles_dir else DEFAULT_HANDLES_DIR
    if not directory.exists():
        raise FileNotFoundError(f"Handle directory '{directory}' does not exist")
    for handle_path in sorted(directory.glob("*.dhandle.json")):
        yield preview_table(handle_path=handle_path, sample_size=sample_size)


def preview_table(*, handle_path: Path, sample_size: int = DEFAULT_SAMPLE_SIZE) -> TablePreview:
    """Load a data handle and build a preview using DuckDB + Arrow."""

    with handle_path.open(encoding="utf-8") as fh:
        handle_data: dict[str, Any] = json.load(fh)

    offline_fallback = handle_data.get("offline_fallback")
    offline_format = (handle_data.get("offline_format") or handle_data.get("format") or "").lower()

    arrow_table: pa.Table | None = None
    sampling_error: str | None = None
    if offline_fallback:
        offline_path = resolve_data_path(offline_fallback)
        try:
            arrow_table = sample_with_duckdb(
                offline_path=offline_path,
                file_format=offline_format,
                sample_size=sample_size,
            )
        except Exception as exc:  # pragma: no cover - defensive
            sampling_error = str(exc)

    schema_metadata = build_schema_metadata(arrow_table=arrow_table, handle_data=handle_data)
    rows = arrow_table.to_pylist() if arrow_table is not None else []

    metadata = {
        "uri": handle_data.get("uri"),
        "format": handle_data.get("format"),
        "offlineFallback": offline_fallback,
        "offlineFormat": offline_format or None,
        "columns": handle_data.get("schema", {}).get("columns"),
        "sampleSize": arrow_table.num_rows if arrow_table is not None else 0,
        "samplingError": sampling_error,
    }

    return TablePreview(
        name=handle_path.name.replace(".dhandle.json", ""),
        handle_path=handle_path,
        schema=schema_metadata,
        rows=rows,
        metadata=metadata,
    )


def resolve_data_path(candidate: str) -> Path:
    """Resolve a data path relative to the repository."""

    candidate_path = Path(candidate)
    resolved = project_path(candidate_path)
    if resolved.exists():
        return resolved

    raise FileNotFoundError(f"Could not resolve data path for '{candidate}'.")


def sample_with_duckdb(*, offline_path: Path, file_format: str, sample_size: int) -> pa.Table:
    """Use DuckDB to sample records from the offline fallback."""

    if not offline_path.exists():
        raise FileNotFoundError(f"Offline fallback '{offline_path}' not found")

    fmt = file_format.lower() if file_format else offline_path.suffix.lstrip(".")

    conn = duckdb.connect(database=":memory:")
    try:
        path_str = offline_path.as_posix().replace("'", "''")
        if fmt in {"csv", "tsv"}:
            query = (
                "SELECT * FROM read_csv_auto('" + path_str + "') LIMIT " + str(sample_size)
            )
        elif fmt in {"parquet", "pqt", "feather"}:
            query = (
                "SELECT * FROM read_parquet('" + path_str + "') LIMIT " + str(sample_size)
            )
        else:
            raise ValueError(
                f"Unsupported offline format '{fmt}' for DuckDB sampling."
            )
        reader = conn.execute(query).arrow()
        return reader.read_all()
    finally:
        conn.close()


def build_schema_metadata(
    *, arrow_table: pa.Table | None, handle_data: dict[str, Any]
) -> list[dict[str, str]]:
    """Combine runtime schema with handle metadata."""

    if arrow_table is not None and len(arrow_table.schema) > 0:
        return [
            {"name": field.name, "type": str(field.type)}
            for field in arrow_table.schema
        ]

    columns = handle_data.get("schema", {}).get("columns", {})
    return [{"name": name, "type": dtype} for name, dtype in columns.items()]
