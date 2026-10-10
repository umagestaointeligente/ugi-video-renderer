"""Verify actual workflow steps, rather than accepting a guard in a comment."""
from pathlib import Path
import sys
import yaml
from validate_workflow_config import WorkflowLoader

GUARD = "python scripts/cena_certa_render_evidence_guard.py "


def check(text):
    errors = []
    doc = yaml.load(text, Loader=WorkflowLoader)
    for job_id, job in doc.get("jobs", {}).items():
        guarded = False
        for step in job.get("steps", []):
            run = step.get("run", "")
            active = [line.strip() for line in run.splitlines() if not line.lstrip().startswith("#")]
            gate_indices = [i for i, line in enumerate(active) if line.startswith(GUARD)]
            gate = bool(gate_indices)
            if gate:
                if step.get("continue-on-error") in (True, "true") or step.get("if") not in (None, "success()", "${{ success() }}"):
                    errors.append(f"{job_id}:EVIDENCE_GUARD_CAN_BE_BYPASSED")
                elif active[:gate_indices[0]] != ["set -euo pipefail"]:
                    errors.append(f"{job_id}:EVIDENCE_GUARD_EXIT_NOT_ENFORCED")
                else:
                    guarded = True
            mutation = any("gh release upload" in line or "gh release create" in line or "gh issue create" in line for line in active)
            if mutation and not guarded:
                errors.append(f"{job_id}:EXTERNAL_WRITE_BEFORE_EVIDENCE_GUARD")
            if mutation and (step.get("continue-on-error") in (True, "true") or step.get("if") not in (None, "success()", "${{ success() }}")):
                errors.append(f"{job_id}:EXTERNAL_WRITE_CAN_IGNORE_FAILURE")
            if mutation and "--clobber" in run:
                errors.append(f"{job_id}:HISTORICAL_RELEASE_OVERWRITE_FORBIDDEN")
    return errors


def main():
    root = Path(__file__).resolve().parents[1]
    checked = 0
    errors = []
    for path in sorted((root / ".github/workflows").glob("cena-certa-*.y*ml")):
        text = path.read_text()
        if "gh release upload" not in text:
            continue
        checked += 1
        errors.extend(f"{path.name}:{e}" for e in check(text))
    for error in errors:
        print(error)
    print(f"CENA_CERTA_RELEASE_BARRIERS={'BLOCK' if errors else 'PASS'} workflows={checked}")
    return bool(errors) or checked == 0


if __name__ == "__main__":
    sys.exit(main())
