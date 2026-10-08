import re
import zipfile
from pathlib import Path
from collections.abc import Mapping
from typing import Any
import xml.etree.ElementTree as ET


LATTES_ID_PATTERN = re.compile(r"(?<!\d)(\d{16})(?!\d)")


def extract_lattes_id(value: object) -> str | None:
    match = LATTES_ID_PATTERN.search(str(value or ""))
    return match.group(1) if match else None


def _xml_lattes_id(path: Path) -> str | None:
    if not path.is_file() or path.suffix.lower() not in {".xml", ".zip"}:
        return None

    try:
        if path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as archive:
                xml_names = [
                    name for name in archive.namelist()
                    if name.lower().endswith(".xml")
                ]
                if not xml_names:
                    return None
                root = ET.fromstring(archive.read(xml_names[0]))
        else:
            root = ET.parse(path).getroot()
    except (OSError, ET.ParseError, zipfile.BadZipFile):
        return None

    for key, value in root.attrib.items():
        if (
            "NUMERO-IDENTIFICADOR" in key.upper()
            or "IDENTIFICADOR" in key.upper()
        ):
            identifier = extract_lattes_id(value)
            if identifier:
                return identifier
    return extract_lattes_id(root.attrib.get("id"))


def resolve_identifier(
    professor: Mapping[str, Any],
    dashboard_backend_root: Path,
) -> dict[str, Any]:
    direct_id = extract_lattes_id(professor.get("lattes_id"))
    if direct_id:
        return _resolved(professor, direct_id, "lattes_id")

    url_id = extract_lattes_id(professor.get("lattes_url"))
    if url_id:
        return _resolved(professor, url_id, "lattes_url")

    relative_xml = professor.get("lattes_xml_path")
    if relative_xml:
        xml_path = (
            dashboard_backend_root / "storage" / "app" / str(relative_xml)
        )
        xml_id = _xml_lattes_id(xml_path)
        if xml_id:
            return _resolved(professor, xml_id, "lattes_xml_path")

    return {
        "database_id": professor.get("id"),
        "name": professor.get("name", ""),
        "lattes_id": None,
        "source": None,
        "status": "missing",
        "reason": (
            "Nenhum ID Lattes válido encontrado em lattes_id, "
            "lattes_url ou XML."
        ),
    }


def _resolved(
    professor: Mapping[str, Any],
    identifier: str,
    source: str,
) -> dict[str, Any]:
    return {
        "database_id": professor.get("id"),
        "name": professor.get("name", ""),
        "lattes_id": identifier,
        "source": source,
        "status": "ready",
        "reason": None,
    }
