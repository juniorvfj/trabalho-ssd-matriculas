"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Testes de integração — modelo SIGAA.

Exercitam os serviços de entidade e o serviço de tarefa verificarElegibilidade
sobre a massa de dados de referência do professor (carregada pelo conftest).
"""
import pytest
from sqlalchemy import select

from app.modules.alunos.infrastructure.orm_models import AlunoCurso
from app.modules.curriculos.infrastructure.orm_models import CurriculoDisciplina

# Aluno de referência presente no DML do professor (curso 6351 — Eng. de Redes)
ALUNO = "180012345"


@pytest.mark.asyncio
async def test_unidade_search_retorna_searchset(client):
    """A pesquisa de unidades devolve o envelope SearchSet com as 14 unidades do professor."""
    r = await client.get("/api/UnidadeOrganizacional/?_count=5")
    assert r.status_code == 200
    body = r.json()
    assert body["resourceType"] == "SearchSet"
    assert body["total"] == 14
    assert len(body["items"]) == 5
    assert all(i["resourceType"] == "UnidadeOrganizacional" for i in body["items"])


@pytest.mark.asyncio
async def test_curso_detalhe_inclui_unidades(client):
    """O detalhe do curso 6351 traz nome, grau e a unidade organizacional vinculada (ENE)."""
    r = await client.get("/api/Curso/6351")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "6351"
    assert "REDES" in body["nome"]
    assert body["grauAcademico"] == "BACHAREL"
    assert "ENE" in [u["id"] for u in body["unidades"]]


@pytest.mark.asyncio
async def test_aluno_detalhe_traz_vinculo(client):
    """O detalhe do aluno traz curso, currículo, IRA e período de ingresso do vínculo."""
    r = await client.get(f"/api/Aluno/{ALUNO}")
    assert r.status_code == 200
    body = r.json()
    assert body["nome"] == "ADA LOVELACE"
    assert body["curso"]["id"] == "6351"
    assert body["curriculo"] == "6351/2"
    assert body["ira"] == pytest.approx(4.76)
    assert body["periodoIngresso"] == {"ano": "2018", "numero": "2"}


@pytest.mark.asyncio
async def test_aluno_search_por_curso(client):
    """A pesquisa por curso retorna os 10 alunos de Engenharia de Redes (6351)."""
    r = await client.get("/api/Aluno/?curso=6351&_count=100")
    assert r.status_code == 200
    assert r.json()["total"] == 10


@pytest.mark.asyncio
async def test_elegibilidade_disciplina_no_curriculo(client, db_session):
    """
    Regra §7.1: aluno sem histórico é elegível para uma disciplina do seu currículo
    (pertence ao currículo, não foi aprovado, e sem pré-requisitos pendentes).
    """
    curriculo = (
        await db_session.execute(select(AlunoCurso.curriculo).where(AlunoCurso.aluno == ALUNO))
    ).scalars().first()
    # Uma disciplina qualquer pertencente ao currículo do aluno
    disciplina = (
        await db_session.execute(
            select(CurriculoDisciplina.disciplina).where(CurriculoDisciplina.curriculo == curriculo)
        )
    ).scalars().first()

    r = await client.post(
        "/api/Tarefa/verificar-elegibilidade", json={"aluno": ALUNO, "disciplina": disciplina}
    )
    assert r.status_code == 200
    assert r.json()["elegivel"] is True


@pytest.mark.asyncio
async def test_elegibilidade_fora_do_curriculo(client, db_session):
    """Regra §7.1: disciplina fora do currículo do aluno torna-o inelegível, com motivo."""
    curriculo = (
        await db_session.execute(select(AlunoCurso.curriculo).where(AlunoCurso.aluno == ALUNO))
    ).scalars().first()
    do_curriculo = set(
        (
            await db_session.execute(
                select(CurriculoDisciplina.disciplina).where(CurriculoDisciplina.curriculo == curriculo)
            )
        ).scalars().all()
    )
    from app.modules.disciplinas.infrastructure.orm_models import Disciplina

    todas = set((await db_session.execute(select(Disciplina.id))).scalars().all())
    fora = next(iter(todas - do_curriculo))

    r = await client.post(
        "/api/Tarefa/verificar-elegibilidade", json={"aluno": ALUNO, "disciplina": fora}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["elegivel"] is False
    assert any("currículo" in m for m in body["motivos"])


@pytest.mark.asyncio
async def test_disciplina_detalhe_carga_total(client, db_session):
    """O detalhe da disciplina soma a carga horária teórica + prática (cargaHorariaTotal)."""
    from app.modules.disciplinas.infrastructure.orm_models import Disciplina

    disc = (await db_session.execute(select(Disciplina))).scalars().first()
    r = await client.get(f"/api/Disciplina/{disc.id}")
    assert r.status_code == 200
    body = r.json()
    esperado = (int(disc.carga_horaria_teorica or 0)) + (int(disc.carga_horaria_pratica or 0))
    assert body["cargaHorariaTotal"] == esperado


@pytest.mark.asyncio
async def test_disciplina_carga_horaria_persistida(client):
    """A coluna carga_horaria (nova) é aceita no POST e devolvida no GET de detalhe."""
    # Cria uma disciplina informando a carga horária total explicitamente.
    payload = {
        "id": "TST0001",
        "nome": "Disciplina de Teste",
        "modalidade": "Presencial",
        "carga_horaria_teorica": 30,
        "carga_horaria_pratica": 30,
        "carga_horaria": 90,
        "unidade": "CIC",  # unidade presente no DML do professor
    }
    r = await client.post("/api/Disciplina/", json=payload)
    assert r.status_code == 201
    assert r.json()["carga_horaria"] == 90

    # O detalhe usa a carga horária informada (90), não a soma teórica+prática (60).
    detalhe = (await client.get("/api/Disciplina/TST0001")).json()
    assert detalhe["cargaHoraria"] == 90
    assert detalhe["cargaHorariaTotal"] == 90
