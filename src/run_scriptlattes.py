import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from .config import Settings, load_settings


CONFIG_KEY_PATTERN = re.compile(r"^\s*{key}\s*=.*$", re.MULTILINE)


def run_scriptlattes(settings: Settings) -> Path:
    settings.prepare_directories()
    data_list = settings.input_dir / "data.list"
    if not data_list.is_file():
        raise FileNotFoundError(
            f"Arquivo de entrada não encontrado: {data_list}"
        )
    if not settings.scriptlattes_root.is_dir():
        raise FileNotFoundError(
            f"ScriptLattes não encontrado: {settings.scriptlattes_root}"
        )
    if not settings.scriptlattes_config_template.is_file():
        raise FileNotFoundError(
            "Configuração do ScriptLattes não encontrada: "
            f"{settings.scriptlattes_config_template}"
        )

    run_dir = settings.output_dir / datetime.now().strftime(
        "run-%Y%m%d-%H%M%S"
    )
    run_dir.mkdir(parents=True, exist_ok=False)
    config_path = run_dir / "data.config"
    config = settings.scriptlattes_config_template.read_text(encoding="utf-8")
    config = _set_config(config, "global-arquivo_de_entrada", data_list)
    config = _set_config(config, "global-diretorio_de_saida", run_dir)
    config = _set_config(
        config,
        "global-diretorio_de_armazenamento_de_cvs",
        run_dir / "cache",
    )
    config = _set_config(
        config,
        "global-salvar_informacoes_em_formato_xml",
        "sim",
    )
    config = _set_config(config, "global-prefixo", "")
    config = _set_config(config, "relatorio-incluir_projeto", "sim")
    config = _set_config(
        config,
        "grafo-mostrar_grafo_de_colaboracoes",
        "nao",
    )
    config_path.write_text(config, encoding="utf-8")

    command = [
        sys.executable,
        "-c",
        (
            "from scriptLattesRunner import ScriptLattesRunner; "
            "import sys; sys.tracebacklimit = None; "
            f"ScriptLattesRunner({str(config_path)!r}).executar()"
        ),
    ]
    log_path = run_dir / "scriptlattes.log"
    with log_path.open("w", encoding="utf-8") as log:
        subprocess.run(
            command,
            cwd=settings.scriptlattes_root,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            check=True,
        )

    database_path = run_dir / "database.xml"
    if not database_path.is_file():
        raise FileNotFoundError(f"O ScriptLattes não gerou: {database_path}")
    return database_path


def _set_config(content: str, key: str, value: str | Path) -> str:
    rendered = Path(value).as_posix() if isinstance(value, Path) else value
    line = f"{key} = {rendered}"
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*=.*$", re.MULTILINE)
    if pattern.search(content):
        return pattern.sub(line, content, count=1)
    return f"{content.rstrip()}\n{line}\n"


if __name__ == "__main__":
    print(run_scriptlattes(load_settings()))
