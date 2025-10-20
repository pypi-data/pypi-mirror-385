import json
import pathlib

from app.code.lib.steps.metrics import run as met_run
from app.code.lib.steps.segment import run as seg_run


def test_segment_and_metrics(tmp_path: pathlib.Path) -> None:
    out_processed = tmp_path / "processed.parquet"
    seg_run("app/data/handles/data.parquet.dhandle.json", str(out_processed))
    out_met = tmp_path / "metrics.json"
    met_run(str(out_processed), "app/data/handles/data.parquet.dhandle.json", str(out_met))
    met = json.loads(out_met.read_text())
    assert met["n"] == 10
    assert met["f1"] >= 0.99
