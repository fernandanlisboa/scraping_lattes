import csv
import xml.etree.ElementTree as ET
from pathlib import Path


PROJECT_FIELDS = [
    "lattes_id",
    "professor",
    "ano_inicio",
    "ano_conclusao",
    "projeto",
    "descricao",
]


def export_projects(xml_path: Path, csv_path: Path) -> int:
    root = ET.parse(xml_path).getroot()
    rows: list[dict[str, str]] = []

    for researcher in root.findall("pesquisador"):
        lattes_id = researcher.attrib.get("id", "")
        professor = researcher.findtext(
            "identificacao/nome_completo",
            default="",
        )
        for project in researcher.findall("projetos_pesquisa/projeto"):
            rows.append(
                {
                    "lattes_id": lattes_id,
                    "professor": professor,
                    "ano_inicio": project.findtext("ano_inicio", default=""),
                    "ano_conclusao": project.findtext(
                        "ano_conclusao",
                        default="",
                    ),
                    "projeto": project.findtext("nome", default=""),
                    "descricao": project.findtext("descricao", default=""),
                }
            )

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=PROJECT_FIELDS, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("xml", type=Path)
    parser.add_argument("csv", type=Path)
    args = parser.parse_args()
    print(f"Projetos exportados: {export_projects(args.xml, args.csv)}")
