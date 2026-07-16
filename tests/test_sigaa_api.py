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
    """O detalhe do aluno segue o Aluno.yml do professor: Curriculo_Short e PeriodoLetivo."""
    r = await client.get(f"/api/Aluno/{ALUNO}")
    assert r.status_code == 200
    body = r.json()
    assert body["nome"] == "ADA LOVELACE"
    assert body["curso"]["id"] == "6351"
    # curriculo é um Curriculo_Short com o id na convenção pública ('6351.2')
    assert body["curriculo"]["id"] == "6351.2"
    assert body["ira"] == pytest.approx(4.76)
    # periodoIngresso é o objeto PeriodoLetivo {ano, periodo} (numérico)
    assert body["periodoIngresso"] == {"ano": 2018, "periodo": 2}


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
    """
    O detalhe da disciplina segue o diagrama: cargaHorariaTotal derivada (teórica + prática)
    e a associação cargaHorariaPresencial como objeto CargaHoraria {teorica, pratica,
    extensionista} — extensionista sempre null (sem coluna no DDL do professor).
    """
    from app.modules.disciplinas.infrastructure.orm_models import Disciplina

    disc = (await db_session.execute(select(Disciplina))).scalars().first()
    r = await client.get(f"/api/Disciplina/{disc.id}")
    assert r.status_code == 200
    body = r.json()
    teorica = int(disc.carga_horaria_teorica or 0)
    pratica = int(disc.carga_horaria_pratica or 0)
    assert body["cargaHorariaTotal"] == teorica + pratica
    # A carga horária é um objeto (associação do diagrama), não campos planos
    assert body["cargaHorariaPresencial"]["teorica"] == teorica
    assert body["cargaHorariaPresencial"]["pratica"] == pratica
    assert body["cargaHorariaPresencial"]["extensionista"] is None
    assert body["cargaHorariaEad"] is None  # massa do professor: tudo presencial
    assert "cargaHorariaTeorica" not in body  # o campo plano não vaza mais
    assert body["unidadeOrganizacional"]["id"] == disc.unidade


@pytest.mark.asyncio
async def test_disciplina_carga_horaria_persistida(client):
    """
    A coluna carga_horaria (exemplo didático do projeto) é aceita no POST e participa
    apenas da derivação de cargaHorariaTotal — não vaza como campo plano na resposta.
    """
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
    # O POST já devolve a representação conceitual, com o total informado prevalecendo
    assert r.json()["cargaHorariaTotal"] == 90

    # O detalhe usa a carga horária informada (90), não a soma teórica+prática (60).
    detalhe = (await client.get("/api/Disciplina/TST0001")).json()
    assert detalhe["cargaHorariaTotal"] == 90
    assert detalhe["cargaHorariaPresencial"] == {"teorica": 30, "pratica": 30, "extensionista": None}
    assert "cargaHoraria" not in detalhe  # a coluna física não aparece com nome próprio


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
    # As disciplinas cursadas são Disciplina_HistoricoAcademico (herança): o item É uma
    # Disciplina (id, nome, cargas) acrescida de mencao/status/periodoLetivo.
    por_disciplina = {i["id"]: i for i in body["disciplina"]}
    assert por_disciplina[discs[0]]["status"] == "aprovado"
    assert por_disciplina[discs[1]]["status"] == "reprovado"
    # Campos herdados da Disciplina base presentes no item especializado
    assert por_disciplina[discs[0]]["cargaHorariaTotal"] is not None
    assert por_disciplina[discs[0]]["periodoLetivo"] == {"ano": 2018, "periodo": 2}

    # Cargas consolidadas derivadas: integralizadas = Σ das aprovadas; pendente = mínimo − Σ
    assert body["cargaHorariaIntegralizadas"] == por_disciplina[discs[0]]["cargaHorariaTotal"]
    assert body["cargaHorariaPendente"] is not None
    assert body["status"] == "ativo"  # STATUS 'A' do vínculo → domínio conceitual
    assert body["aluno"]["curso"]["id"] == "6351"


@pytest.mark.asyncio
async def test_curriculo_disciplinas_como_disciplina_curriculo(client, db_session):
    """
    Os componentes curriculares são Disciplina_Curriculo (herança de Disciplina):
    carregam os campos herdados (nome, cargas) mais 'nivel' (coluna PERIODO) e o
    'tipo' legível ('OBR' → 'Obrigatória'), como no SIGAA-API.sql do professor.
    """
    curriculo = (
        await db_session.execute(select(AlunoCurso.curriculo).where(AlunoCurso.aluno == ALUNO))
    ).scalars().first()
    url_id = curriculo.replace("/", ".")  # convenção pública do professor: '6351.2'

    body = (await client.get(f"/api/Curriculo/{url_id}/disciplina")).json()
    assert body["total"] > 0
    item = body["items"][0]
    assert item["tipo"] in {"Obrigatória", "Optativa"}
    # 'nivel' vem da coluna PERIODO (nula para optativas sem semestre sugerido)
    assert any(isinstance(i["nivel"], int) for i in body["items"])
    # Herança: o componente É uma Disciplina — campos da base presentes
    assert item["resourceType"] == "Disciplina"
    assert item["nome"]
    assert item["cargaHorariaTotal"] is not None

    filtrado = (await client.get(f"/api/Curriculo/{url_id}/disciplina?tipo=Obrigatória")).json()
    assert filtrado["total"] > 0
    assert all(i["tipo"] == "Obrigatória" for i in filtrado["items"])


@pytest.mark.asyncio
async def test_curriculo_detalhe_carga_horaria_e_prazo_como_objetos(client, db_session):
    """
    O detalhe do currículo segue o diagrama: 'cargaHoraria' (CargaHoraria) e 'prazo'
    (Prazo) como objetos de valor e 'periodoLetivoVigor' como PeriodoLetivo — em vez
    das colunas planas CARGA_HORARIA_* / MIN_PERIODOS / NUM_PERIODOS / MAX_PERIODOS.
    """
    from app.modules.curriculos.infrastructure.orm_models import Curriculo

    c = (await db_session.execute(select(Curriculo))).scalars().first()
    url_id = c.id.replace("/", ".")

    body = (await client.get(f"/api/Curriculo/{url_id}")).json()
    assert body["id"] == url_id
    assert body["status"] in {"ativo", "inativo"}  # domínio conceitual, não 'A'/'I'
    assert body["periodoLetivoVigor"]["ano"] == int(c.periodo_letivo_vigor[:4])

    carga = body["cargaHoraria"]
    assert carga["totalMinima"] == int(c.carga_horaria_minima_total)
    assert carga["obrigatoriaTotal"] == int(c.carga_horaria_obr)
    assert carga["optativaMinima"] == int(c.carga_horaria_minima_opt)
    assert carga["maximaEletivos"] == int(c.carga_horaria_eletiva_max)
    assert carga["maximaPeriodo"] == int(c.carga_horaria_max_periodo)
    assert carga["minimaPeriodo"] is None  # sem coluna no DDL → null documentado

    prazo = body["prazo"]
    assert prazo["minimo"] == int(c.min_periodos)
    assert prazo["medio"] == int(c.num_periodos)
    assert prazo["maximo"] == int(c.max_periodos)
