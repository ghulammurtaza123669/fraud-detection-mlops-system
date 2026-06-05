import json
from datetime import UTC, datetime
from pathlib import Path


def write_metadata(path: Path, *, model_version: str, metrics: dict, params: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model_version": model_version,
        "created_at": datetime.now(UTC).isoformat(),
        "metrics": metrics,
        "params": params,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_metadata(path: Path) -> dict:
    if not path.exists():
        return {"model_version": "untrained"}
    return json.loads(path.read_text(encoding="utf-8"))
