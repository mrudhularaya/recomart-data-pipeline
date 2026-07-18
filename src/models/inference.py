"""Simple local inference interface for the latest saved content-based recommendations."""

import json
import sys
from pathlib import Path
from typing import List


def recommend_for_user(user_id: str, top_k: int = 5, artifact_path: Path | None = None) -> List[str]:
    path = artifact_path or Path(__file__).resolve().parents[2] / "artifacts" / "recommendations.json"
    if not path.exists():
        raise FileNotFoundError("Recommendation artifact is missing. Run src/models/trainer.py first.")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload["recommendations"].get(str(user_id), [])[:top_k]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python src/models/inference.py <user_id> [top_k]")
    print(json.dumps(recommend_for_user(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 5), indent=2))
