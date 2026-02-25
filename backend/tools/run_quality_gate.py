import argparse
import glob
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from main import CodeInspectorApp
from tools.compare_reference_report import compare as compare_reports


def _run_tests() -> bool:
    cmd = [
        sys.executable,
        "-m",
        "unittest",
        "backend.system_verification",
        "backend.tests.test_api_and_reports",
        "backend.tests.test_todo_rule_mining",
        "backend.tests.test_winccoa_context_server",
    ]
    proc = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True)
    print(proc.stdout)
    if proc.returncode != 0:
        print(proc.stderr)
        return False
    return True


def _find_reference(data_dir: Path) -> Path:
    pattern = str(data_dir / "(코드리뷰결과서-Server) 코드 리뷰 결과서-HMI_천안 HVAC 유지보수_GoldenTime_3차_*.xlsx")
    candidates = sorted(glob.glob(pattern))
    if not candidates:
        raise FileNotFoundError("GoldenTime reference workbook not found")
    return Path(candidates[-1])


def _find_generated(output_dir: Path) -> Path:
    pattern = str(output_dir / "CodeReview_Submission_GoldenTime_*.xlsx")
    candidates = sorted(glob.glob(pattern))
    if not candidates:
        raise FileNotFoundError("Generated GoldenTime workbook not found")
    return Path(candidates[-1])


def run_quality_gate(data_dir: Path, mismatch_threshold: int, run_tests: bool) -> int:
    if run_tests and not _run_tests():
        print("[!] Quality gate failed: unit/integration tests failed")
        return 2

    golden_ctl = data_dir / "GoldenTime.ctl"
    if not golden_ctl.exists():
        print(f"[!] Quality gate failed: missing {golden_ctl}")
        return 3

    reference_path = _find_reference(data_dir)

    app = CodeInspectorApp()
    app.data_dir = str(data_dir)
    result = app.run_directory_analysis(
        mode="Static",
        selected_files=["GoldenTime.ctl"],
        enable_ctrlppcheck=False,
        enable_live_ai=False,
    )

    output_dir = Path(str(result.get("output_dir", ""))).resolve()
    generated_path = _find_generated(output_dir)

    compare_result = compare_reports(str(reference_path), str(generated_path))
    report_path = output_dir / "goldentime_compare_result.json"
    report_path.write_text(json.dumps(compare_result, ensure_ascii=False, indent=2), encoding="utf-8")

    mismatch = int(compare_result.get("mismatch_count", 999))
    print(f"[+] GoldenTime mismatch_count={mismatch} (threshold={mismatch_threshold})")
    print(f"[+] Compare report: {report_path}")

    if mismatch > mismatch_threshold:
        print("[!] Quality gate failed: mismatch threshold exceeded")
        return 4

    print("[+] Quality gate passed")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Run quality gate with tests + GoldenTime reference comparison.")
    parser.add_argument(
        "--data-dir",
        default=str(PROJECT_ROOT / "CodeReview_Data"),
        help="Directory containing GoldenTime.ctl and reference workbook",
    )
    parser.add_argument("--mismatch-threshold", type=int, default=5, help="Allowed mismatch count")
    parser.add_argument("--skip-tests", action="store_true", help="Skip unittest phase")
    args = parser.parse_args()

    code = run_quality_gate(
        data_dir=Path(args.data_dir).resolve(),
        mismatch_threshold=args.mismatch_threshold,
        run_tests=not args.skip_tests,
    )
    raise SystemExit(code)


if __name__ == "__main__":
    main()
