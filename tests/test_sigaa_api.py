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


# ── Campos do modelo conceitual derivados do schema do professor (Grupo B) ──────


async def _turma_de_teste(client, db_session, codigo: str, vagas: int = 40) -> dict:
    """Abre uma turma para uma disciplina qualquer do DML do professor."""
    from app.modules.disciplinas.infrastructure.orm_models import Disciplina

    disc = (await db_session.execute(select(Disciplina))).scalars().first()
    r = await client.post(
        "/api/Turma/",
        json={"codigo": codigo, "periodo_letivo": "20182", "disciplina": disc.id, "vagas": vagas},
    )
    assert r.status_code == 201
    return r.json()


@pytest.mark.asyncio
async def test_matricula_motivo_indeferimento_derivado_do_status(client, db_session):
    """
    B1: no SIGAA o motivo do indeferimento não é coluna — é o próprio status. A descrição
    legível vem de SIGAA_MATRICULA_STATUS e só é exposta em status de indeferimento.
    """
    turma = await _turma_de_teste(client, db_session, "01")

    criadas = (
        await client.post("/api/Matricula/", json=[{"aluno": ALUNO, "turma": turma["id"]}])
    ).json()
    # Um pedido (PND) não é indeferimento: não há motivo.
    assert criadas[0]["motivoIndeferimento"] is None
    assert criadas[0]["statusDescricao"] == "Pedido"

    r = await client.patch(
        f"/api/Matricula/{criadas[0]['id']}",
        json=[{"op": "replace", "path": "/status", "value": "CON"}],
    )
    assert r.status_code == 200
    assert r.json()["motivoIndeferimento"] == "Conflito de horário"


@pytest.mark.asyncio
async def test_turma_vagas_ofertadas_e_preenchidas(client, db_session):
    """B3: o SIGAA só tem a coluna VAGAS; vagasPreenchidas é derivado das matrículas 'MAT'."""
    turma = await _turma_de_teste(client, db_session, "02", vagas=40)

    body = (await client.get(f"/api/Turma/{turma['id']}")).json()
    assert body["vagasOfertadas"] == 40
    assert body["vagasPreenchidas"] == 0

    criadas = (
        await client.post("/api/Matricula/", json=[{"aluno": ALUNO, "turma": turma["id"]}])
    ).json()
    await client.patch(
        f"/api/Matricula/{criadas[0]['id']}",
        json=[{"op": "replace", "path": "/status", "value": "MAT"}],
    )

    body = (await client.get(f"/api/Turma/{turma['id']}")).json()
    assert body["vagasOfertadas"] == 40
    assert body["vagasPreenchidas"] == 1


@pytest.mark.asyncio
async def test_historico_status_derivado_da_mencao(client, db_session):
    """B9: o histórico não tem coluna de status — é derivado da menção (SS/MS/MM aprovam)."""
    vinculo = (
        await db_session.execute(select(AlunoCurso.id).where(AlunoCurso.aluno == ALUNO))
    ).scalars().first()
    curriculo = (
        await db_session.execute(select(AlunoCurso.curriculo).where(AlunoCurso.aluno == ALUNO))
    ).scalars().first()
    discs = (
        await db_session.execute(
            select(CurriculoDisciplina.disciplina).where(CurriculoDisciplina.curriculo == curriculo)
        )
    ).scalars().all()

    for disciplina, mencao in ((discs[0], "SS"), (discs[1], "SR")):
        r = await client.post(
            "/api/HistoricoAcademico/disciplina",
            json={
                "aluno_curso": vinculo,
                "disciplina": disciplina,
                "periodo_letivo": "20182",
                "mencao": mencao,
            },
        )
        assert r.status_code == 201

    body = (await client.get(f"/api/HistoricoAcademico/{ALUNO}")).json()
    por_disciplina = {i["disciplina"]["id"]: i for i in body["disciplinas"]}
    assert por_disciplina[discs[0]]["status"] == "Aprovado"
    assert por_disciplina[discs[1]]["status"] == "Reprovado"


@pytest.mark.asyncio
async def test_curriculo_disciplinas_expoe_nivel_e_tipo_legivel(client, db_session):
    """
    O SIGAA-API.sql do professor expõe a coluna PERIODO como 'nivel' e traduz o tipo
    ('OBR' → 'Obrigatória'); o filtro por tipo aceita o rótulo legível.
    """
    curriculo = (
        await db_session.execute(select(AlunoCurso.curriculo).where(AlunoCurso.aluno == ALUNO))
    ).scalars().first()
    url_id = curriculo.replace("/", "")

    body = (await client.get(f"/api/Curriculo/{url_id}/disciplinas")).json()
    assert body["total"] > 0
    item = body["items"][0]
    assert item["nivel"] == item["periodo"]
    assert item["tipo"] in {"Obrigatória", "Optativa"}
    assert item["tipoCodigo"] in {"OBR", "OPT"}

    filtrado = (await client.get(f"/api/Curriculo/{url_id}/disciplinas?tipo=Obrigatória")).json()
    assert filtrado["total"] > 0
    assert all(i["tipo"] == "Obrigatória" for i in filtrado["items"])
