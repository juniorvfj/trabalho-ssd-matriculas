"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Módulo: Seed (Carga Inicial de Dados) — modelo SIGAA

Responsável por popular o banco com a massa de dados de referência fornecida pelo
professor nos scripts DML de `professor_material/database/`. Como as tabelas do
projeto foram alinhadas ao schema SIGAA, o DML do professor é carregado
praticamente VERBATIM (sem transformação/ETL).

Ordem de carga (respeitando as dependências de chave estrangeira do professor):
  1. SIGAA-DDL - novo.sql ............ apenas os INSERTs (horário de aula + status de matrícula)
  2. SIGAA-DML-DisciplinaCurso - novo.sql ... unidade, curso, currículo, disciplina, pré-requisitos
  3. SIGAA-DatabaseDML_Alunos - novo.sql .... alunos + vínculos aluno-curso

Características:
  - Idempotente: se a base já estiver populada (SIGAA_UNIDADE com linhas), não recarrega.
  - Perene: pensado para rodar a cada boot do container da API, logo após
    `alembic upgrade head` (ver docker-compose.yml). Numa base recém-criada, carrega;
    numa base já populada, apenas confirma e sai.
  - Executa cada INSERT via driver bruto (exec_driver_sql) porque literais de horário
    como '08:00' contêm ':' e seriam confundidos com bind params pelo SQLAlchemy text().
"""
import asyncio
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings

# Diretório com os scripts SQL de referência do professor
DB_DIR = Path(__file__).resolve().parent.parent / "professor_material" / "database"

# Arquivos na ordem de carga que respeita as FKs do modelo SIGAA
DML_FILES = [
    "SIGAA-DDL - novo.sql",                    # só os INSERTs (horarioaula + matricula_status)
    "SIGAA-DML-DisciplinaCurso - novo.sql",
    "SIGAA-DatabaseDML_Alunos - novo.sql",
]


def _extract_inserts(sql_path: Path) -> list[str]:
    """
    Lê um arquivo .sql e retorna apenas os comandos INSERT.

    Descarta comentários de linha (--), CREATE/DROP/SELECT e linhas em branco.
    Assim o mesmo parser serve tanto para o arquivo de DDL (que tem CREATE + INSERT)
    quanto para os arquivos puramente DML.
    """
    raw = sql_path.read_text(encoding="utf-8")
    # Remove comentários de linha para não quebrar o split por ';'
    linhas = [ln for ln in raw.splitlines() if not ln.strip().startswith("--")]
    conteudo = "\n".join(linhas)
    comandos = [c.strip() for c in conteudo.split(";")]
    return [c for c in comandos if c.lower().startswith("insert")]


async def _ja_populado(conn) -> bool:
    """Idempotência: considera a base já semeada se SIGAA_UNIDADE tiver linhas."""
    try:
        total = (await conn.execute(text("SELECT COUNT(*) FROM sigaa_unidade"))).scalar_one()
        return total > 0
    except Exception:
        # Tabela ainda não existe (migrations não aplicadas) — deixa o chamador tratar
        return False


async def seed_data() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    try:
        async with engine.begin() as conn:
            if await _ja_populado(conn):
                print("[seed] Base já populada com os dados SIGAA — nada a fazer (idempotente).")
                return

            total_geral = 0
            for nome in DML_FILES:
                caminho = DB_DIR / nome
                if not caminho.exists():
                    raise FileNotFoundError(
                        f"[seed] Arquivo DML do professor não encontrado: {caminho}"
                    )
                comandos = _extract_inserts(caminho)
                for stmt in comandos:
                    # exec_driver_sql envia o SQL bruto ao asyncpg (preserva ':' em '08:00')
                    await conn.exec_driver_sql(stmt)
                total_geral += len(comandos)
                print(f"[seed] {nome}: {len(comandos)} INSERTs aplicados.")

            print(f"[seed] Carga SIGAA concluída com sucesso — {total_geral} INSERTs no total.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
