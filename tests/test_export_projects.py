from pathlib import Path

from src.export_projects import export_projects


def test_export_projects_from_fixture(tmp_path: Path) -> None:
    xml_path = Path(__file__).parent / "fixtures" / "database.example.xml"
    csv_path = tmp_path / "projetos.csv"

    count = export_projects(xml_path, csv_path)

    assert count == 1
    content = csv_path.read_text(encoding="utf-8-sig")
    assert "Professora Exemplo" in content
    assert "Projeto de Pesquisa, com vírgula" in content
