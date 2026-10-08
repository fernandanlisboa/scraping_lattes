# Scraping Lattes

Pipeline Python externa ao dashboard para:

1. obter uma lista local de nomes;
2. localizar os professores na página oficial do corpo docente;
3. gerar a lista de entrada do ScriptLattes;
4. executar o ScriptLattes em lote;
5. gerar um CSV único com os projetos.

A pasta fica em `f:\Projetos\Mestrado\scraping lattes`, ao lado de `pgcomp-dashboard` e `ScriptLattes`.

## Pré-requisitos

- Python 3.11 ou superior;
- dependências do ScriptLattes instaladas conforme `ScriptLattes/scriptLattes/requirements.txt`;
- ChromeDriver configurado para o ScriptLattes.

## Instalação

No PowerShell:

```powershell
cd "F:\Projetos\Mestrado\scraping lattes"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[test]"
pip install -r "F:\Projetos\Mestrado\ScriptLattes\scriptLattes\requirements.txt"
Copy-Item .env.example .env
```

Ajuste o `.env` com o caminho de `PROFESSORS_NAMES_FILE`. Esta pipeline não acessa o banco do dashboard. `FACULTY_VERIFY_SSL=false` reproduz a configuração do comando Laravel existente; em uma rede com certificados válidos, altere para `true`.

## Fluxo

Crie `data/input/professors-names.txt`, com um professor por linha:

```text
Nome Completo do Professor
Outro Professor
```

A etapa `export` consulta `FACULTY_URL`, atualmente configurada para `https://pgcomp.ufba.br/corpo-docente`, e associa cada nome ao link Lattes encontrado na tabela oficial:

```powershell
python -m src.pipeline export
```

Ela gera `data/input/data.list`, `data/input/professors.json`, `data/output/professors.csv` e `data/output/missing_professors.csv`.

Para executar o ScriptLattes e gerar XML:

```powershell
python -m src.pipeline scrape
```

Para converter o último `database.xml` em CSV:

```powershell
python -m src.pipeline csv
```

Ou executar tudo:

```powershell
python -m src.pipeline all
```

O resultado final fica em:

```text
data/output/projetos-lattes.csv
```

Cada execução do ScriptLattes fica preservada em `data/output/run-YYYYMMDD-HHMMSS/`, incluindo `data.config`, `database.xml`, cache e log.

## Origem e créditos

Esta pipeline não é uma implementação original do zero. Ela foi baseada parcialmente no código, na arquitetura e no fluxo dos seguintes repositórios:

1. [pgcomp-dashboard/ScriptLattes](https://github.com/pgcomp-dashboard/ScriptLattes/tree/main);
2. [pgcomp-dashboard/pgcomp-dashboard](https://github.com/pgcomp-dashboard/pgcomp-dashboard/tree/main).

O código deste repositório adapta esses projetos para um fluxo independente, baseado em uma lista local de professores, sem acesso direto ao banco de dados do dashboard. O desenvolvimento foi realizado em coautoria com GitHub Copilot.

## Origem dos IDs

A pipeline procura cada nome na página oficial do corpo docente e extrai o ID de 16 dígitos do link Lattes encontrado.

Nomes não encontrados, ambíguos ou sem link Lattes não interrompem o lote; eles aparecem em `missing_professors.csv`.

## Filtro de mestrado

O banco atual não define uma relação inequívoca entre professor e programa de mestrado. Por padrão, a pipeline processa todos os usuários com `type = professor`. O filtro opcional pode ser configurado no `.env` com `PROFESSOR_IDS` ou `PROFESSOR_CATEGORIES`.

## Campos do CSV

O CSV contém somente campos fornecidos pelo ScriptLattes para projetos:

- `lattes_id`;
- `professor`;
- `ano_inicio`;
- `ano_conclusao`;
- `projeto`;
- `descricao`.

Campos do dashboard como valor, financiador, status, natureza e função não são inventados porque não fazem parte do objeto `ProjetoDePesquisa` do ScriptLattes.

## Testes

```powershell
pytest
```

Os testes usam apenas o XML sanitizado em `tests/fixtures/database.example.xml` e não acessam o banco nem o CNPq.
