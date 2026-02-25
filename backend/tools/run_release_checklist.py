import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from tools.run_quality_gate import run_quality_gate


def main() -> int:
    """
    Release fixed checklist runner.
    Policy is intentionally fixed:
      - run tests: always ON
      - mismatch threshold: 5
      - data dir: <project>/CodeReview_Data
    """
    data_dir = (PROJECT_ROOT / "CodeReview_Data").resolve()
    return run_quality_gate(data_dir=data_dir, mismatch_threshold=5, run_tests=True)


if __name__ == "__main__":
    raise SystemExit(main())
