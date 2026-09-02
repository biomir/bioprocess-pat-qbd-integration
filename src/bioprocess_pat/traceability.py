import csv
from pathlib import Path

REQUIRED = {"requirement_id", "risk_id", "control_id", "verification_id", "status"}


def validate_traceability(path):
    errors = []
    with Path(path).open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        fields = set(reader.fieldnames or [])
        missing = REQUIRED - fields
        if missing:
            return [f"missing columns: {', '.join(sorted(missing))}"]
        for line_number, row in enumerate(reader, start=2):
            for field in ("requirement_id", "risk_id", "control_id", "verification_id"):
                if not (row.get(field) or "").strip():
                    errors.append(f"line {line_number}: missing {field}")
            if (row.get("status") or "").strip().lower() not in {
                "pass",
                "fail",
                "not_run",
            }:
                errors.append(f"line {line_number}: invalid status")
    return errors
