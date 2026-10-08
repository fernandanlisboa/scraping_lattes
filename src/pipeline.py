import argparse
import json
from pathlib import Path

from .config import load_settings
from .export_projects import export_projects
from .export_professors import export_professors
from .run_scriptlattes import run_scriptlattes


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline de projetos Lattes")
    parser.add_argument(
        "step",
        choices=["export", "scrape", "csv", "all"],
        help="Etapa da pipeline a executar",
    )
    parser.add_argument(
        "--xml",
        type=Path,
        help="XML existente para a etapa csv",
    )
    args = parser.parse_args()
    settings = load_settings()

    if args.step == "export":
        print(
            json.dumps(
                export_professors(settings),
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if args.step == "scrape":
        print(run_scriptlattes(settings))
        return

    if args.step == "csv":
        xml_path = args.xml or _latest_xml(settings.output_dir)
        csv_path = settings.output_dir / "projetos-lattes.csv"
        print(f"Projetos exportados: {export_projects(xml_path, csv_path)}")
        print(csv_path)
        return

    export_professors(settings)
    xml_path = run_scriptlattes(settings)
    csv_path = settings.output_dir / "projetos-lattes.csv"
    print(f"Projetos exportados: {export_projects(xml_path, csv_path)}")
    print(csv_path)


def _latest_xml(output_dir: Path) -> Path:
    files = sorted(output_dir.glob("run-*/database.xml"), reverse=True)
    if not files:
        raise FileNotFoundError(
            "Nenhum database.xml foi encontrado em data/output."
        )
    return files[0]


if __name__ == "__main__":
    main()
