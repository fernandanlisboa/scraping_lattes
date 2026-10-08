from pathlib import Path

from src.faculty import parse_faculty_html
from src.identifiers import extract_lattes_id, resolve_identifier


def test_extract_lattes_id_from_url() -> None:
    assert extract_lattes_id(
        "http://lattes.cnpq.br/1234567890123456"
    ) == "1234567890123456"
    assert extract_lattes_id("sem identificador") is None


def test_resolve_identifier_uses_xml_fallback(tmp_path: Path) -> None:
    backend_root = tmp_path / "backend"
    xml_path = backend_root / "storage" / "app" / "lattes" / "professor.xml"
    xml_path.parent.mkdir(parents=True)
    xml_path.write_text(
        '<CURRICULO-VITAE NUMERO-IDENTIFICADOR="6543210987654321" />',
        encoding="utf-8",
    )

    result = resolve_identifier(
        {
            "id": 1,
            "name": "Professor XML",
            "lattes_id": None,
            "lattes_url": None,
            "lattes_xml_path": "lattes/professor.xml",
        },
        backend_root,
    )

    assert result["lattes_id"] == "6543210987654321"
    assert result["source"] == "lattes_xml_path"


def test_parse_faculty_html_extracts_name_and_lattes() -> None:
    fixture = Path(__file__).parent / "fixtures" / "faculty.example.html"
    html = fixture.read_text(encoding="utf-8")

    professors = parse_faculty_html(html)

    assert professors[0]["name"] == "Professora Exemplo"
    assert professors[0]["lattes_id"] == "1234567890123456"
