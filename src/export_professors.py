import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import Settings, load_settings
from .faculty import professors_from_names


def export_professors(settings: Settings) -> dict[str, Any]:
    records = professors_from_names(settings)
    ready = [record for record in records if record["status"] == "ready"]
    missing = [record for record in records if record["status"] != "ready"]

    json_path = settings.input_dir / "professors.json"
    list_path = settings.input_dir / "data.list"
    found_csv_path = settings.output_dir / "professors.csv"
    missing_csv_path = settings.output_dir / "missing_professors.csv"

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_professors": len(records),
        "ready": len(ready),
        "missing": len(missing),
        "professors": records,
    }
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with list_path.open("w", encoding="utf-8", newline="") as file:
        for record in ready:
            name = " ".join(str(record["name"]).splitlines()).strip()
            file.write(f"{record['lattes_id']} , {name}\n")

    _write_csv(
        found_csv_path,
        ready,
        ["database_id", "name", "lattes_id", "source", "status"],
    )
    _write_csv(
        missing_csv_path,
        missing,
        ["database_id", "name", "lattes_id", "source", "status", "reason"],
    )

    return {
        "total": len(records),
        "ready": len(ready),
        "missing": len(missing),
        "json": str(json_path),
        "data_list": str(list_path),
    }


def _write_csv(
    path: Path,
    rows: list[dict[str, Any]],
    fields: list[str],
) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    result = export_professors(load_settings())
    print(json.dumps(result, ensure_ascii=False, indent=2))
