import re
import unicodedata
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

from .config import Settings
from .identifiers import extract_lattes_id


FACULTY_TABLES = (
    ("Permanente", "permanente"),
    ("Colaborador", "colaborador"),
    ("Visitante", "visitante"),
)


def read_professor_names(path: Path) -> list[str]:
    if not path.is_file():
        raise FileNotFoundError(f"Lista de nomes não encontrada: {path}")
    names = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        name = line.strip()
        if name and not name.startswith("#"):
            names.append(name)
    return names


def fetch_faculty_page(
    url: str,
    verify_ssl: bool = False,
) -> list[dict[str, Any]]:
    response = requests.get(
        url,
        headers={"User-Agent": "pgcomp-scraping-lattes/1.0"},
        timeout=30,
        verify=verify_ssl,
    )
    response.raise_for_status()
    return parse_faculty_html(response.text)


def parse_faculty_html(html: str) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    records = []

    tables = soup.select("div.table-responsive table")
    for index, table in enumerate(tables):
        category = (
            FACULTY_TABLES[index][1]
            if index < len(FACULTY_TABLES)
            else None
        )
        for row in table.select("tbody tr"):
            cells = row.find_all("td")
            if not cells:
                continue
            link = next(
                (
                    anchor.get("href", "")
                    for anchor in row.select("a[href]")
                    if "lattes" in anchor.get("href", "").lower()
                ),
                "",
            )
            name = _clean_name(cells[0].get_text(" ", strip=True))
            if name and link:
                records.append(
                    {
                        "name": name,
                        "lattes_url": link,
                        "lattes_id": extract_lattes_id(link),
                        "category": category,
                    }
                )
    return records


def professors_from_names(settings: Settings) -> list[dict[str, Any]]:
    requested_names = read_professor_names(settings.professors_names_file)
    available = fetch_faculty_page(
        settings.faculty_url,
        verify_ssl=settings.faculty_verify_ssl,
    )
    indexed: dict[str, list[dict[str, Any]]] = {}
    for professor in available:
        indexed.setdefault(
            _normalize_name(professor["name"]),
            [],
        ).append(professor)

    records = []
    for requested_name in requested_names:
        matches = indexed.get(_normalize_name(requested_name), [])
        if len(matches) == 1 and matches[0].get("lattes_id"):
            match = matches[0]
            records.append(
                {
                    "database_id": None,
                    "name": match["name"],
                    "requested_name": requested_name,
                    "lattes_id": match["lattes_id"],
                    "source": "faculty_page",
                    "category": match["category"],
                    "status": "ready",
                    "reason": None,
                }
            )
            continue

        reason = "Nome não encontrado na página do corpo docente."
        if len(matches) > 1:
            reason = (
                "Nome encontrado mais de uma vez na página do corpo docente."
            )
        records.append(
            {
                "database_id": None,
                "name": requested_name,
                "requested_name": requested_name,
                "lattes_id": None,
                "source": None,
                "category": None,
                "status": "missing",
                "reason": reason,
            }
        )
    return records


def _clean_name(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip()


def _normalize_name(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name)
    without_accents = "".join(
        character for character in normalized
        if not unicodedata.combining(character)
    )
    return re.sub(r"\s+", " ", without_accents).strip().casefold()
