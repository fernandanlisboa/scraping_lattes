from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
PROJECTS_ROOT = PIPELINE_ROOT.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    faculty_url: str = "https://pgcomp.ufba.br/corpo-docente"
    faculty_verify_ssl: bool = False
    professors_names_file: Path = (
        PIPELINE_ROOT / "data" / "input" / "professors-names.txt"
    )
    scriptlattes_root: Path = PROJECTS_ROOT / "ScriptLattes" / "scriptLattes"
    scriptlattes_config_template: Path = (
        scriptlattes_root / "config" / "data.config"
    )
    input_dir: Path = PIPELINE_ROOT / "data" / "input"
    output_dir: Path = PIPELINE_ROOT / "data" / "output"

    def prepare_directories(self) -> None:
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)


def load_settings() -> Settings:
    settings = Settings()
    settings.prepare_directories()
    return settings
