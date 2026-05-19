"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Módulo: Testes de Integração — Docentes e Unidades Organizacionais
Descrição: Valida o CRUD das entidades Docente, UnidadeOrganizacional e TurmaDocente,
incluindo as relações com Curso (coordenador_id, unidade_organizacional_id) e
Disciplina (unidade_organizacional_id), conforme o diagrama de entidades.
"""
import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.usuarios.infrastructure.orm_models import Usuario, RoleEnum
from app.core.security import get_password_hash


# ═══════════════════════════════════════════════════════════════════════════════
# Helper: obter token JWT autenticado para endpoints protegidos
# ═══════════════════════════════════════════════════════════════════════════════

async def get_auth_headers(client, db_session):
    """Cria um usuário ADMIN e retorna headers com Bearer token."""
    username = f"admin_{uuid.uuid4().hex[:8]}"
    senha_hash = get_password_hash("test123")
    user = Usuario(id=str(uuid.uuid4()), username=username, hashed_password=senha_hash, role=RoleEnum.ADMIN)
    db_session.add(user)
    await db_session.flush()

    resp = await client.post("/api/v1/auth/login", data={
        "username": username, "password": "test123"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ═══════════════════════════════════════════════════════════════════════════════
# Testes de Docente
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_crud_docente(client):
    """
    Testa o CRUD completo de Docente:
    - POST /api/Docente → cria docente
    - GET /api/Docente → lista docentes
    - GET /api/Docente/{id} → detalha docente
    """
    payload = {"matricula": "DOC001", "nome": "Prof. Ricardo Puttini"}
    resp = await client.post("/api/Docente/", json=payload)
    assert resp.status_code == 201, f"Esperado 201, recebeu {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["matricula"] == "DOC001"
    assert data["nome"] == "Prof. Ricardo Puttini"
    assert data["ativo"] is True
    docente_id = data["id"]

    resp = await client.get("/api/Docente/")
    assert resp.status_code == 200
    assert any(d["id"] == str(docente_id) for d in resp.json()["items"])

    resp = await client.get(f"/api/Docente/{docente_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == str(docente_id)

    resp = await client.get("/api/Docente/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_docente_matricula_duplicada(client):
    """Testa que não é possível criar dois docentes com a mesma matrícula."""
    payload = {"matricula": "DOC_DUP", "nome": "Docente A"}
    resp1 = await client.post("/api/Docente/", json=payload)
    assert resp1.status_code == 201

    resp2 = await client.post("/api/Docente/", json=payload)
    assert resp2.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# Testes de Unidade Organizacional
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_crud_unidade_organizacional(client):
    """
    Testa o CRUD completo de Unidade Organizacional:
    - POST /api/UnidadeOrganizacional → cria UO
    - GET /api/UnidadeOrganizacional → lista UOs
    - GET /api/UnidadeOrganizacional/{id} → detalha UO
    """
    payload = {"codigo": "CIC", "nome": "Departamento de Ciência da Computação"}
    resp = await client.post("/api/UnidadeOrganizacional/", json=payload)
    assert resp.status_code == 201, f"Esperado 201, recebeu {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data["codigo"] == "CIC"
    assert data["nome"] == "Departamento de Ciência da Computação"
    uo_id = data["id"]

    resp = await client.get("/api/UnidadeOrganizacional/")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) >= 1

    resp = await client.get(f"/api/UnidadeOrganizacional/{uo_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == str(uo_id)

    resp = await client.get("/api/UnidadeOrganizacional/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_unidade_codigo_duplicado(client):
    """Testa que não é possível criar duas UOs com o mesmo código."""
    payload = {"codigo": "MAT_DUP", "nome": "Departamento de Matemática"}
    resp1 = await client.post("/api/UnidadeOrganizacional/", json=payload)
    assert resp1.status_code == 201

    resp2 = await client.post("/api/UnidadeOrganizacional/", json=payload)
    assert resp2.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# Testes de TurmaDocente (vinculação N:M)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_vincular_docente_turma(client, db_session):
    """
    Testa a vinculação de um docente a uma turma (relação N:M do diagrama).
    Também valida que vínculo duplicado retorna 409 CONFLICT.
    """
    headers = await get_auth_headers(client, db_session)

    curso_resp = await client.post("/api/Curso/", json={
        "codigo": "CC_TD", "nome": "Ciência da Computação"
    }, headers=headers)
    assert curso_resp.status_code == 201, f"Curso: {curso_resp.text}"
    curso_id = curso_resp.json()["id"]

    disc_resp = await client.post("/api/Disciplina/", json={
        "codigo": "CIC001_TD", "nome": "Algoritmos", "creditos": 4,
        "carga_horaria": 60, "curso_id": curso_id
    }, headers=headers)
    assert disc_resp.status_code == 201, f"Disciplina: {disc_resp.text}"
    disc_id = disc_resp.json()["id"]

    periodo_resp = await client.post("/api/Turma/periodos", json={
        "codigo": "2026.1_TD", "descricao": "Semestre Teste",
        "data_inicio": "2026-03-01", "data_fim": "2026-07-01"
    }, headers=headers)
    assert periodo_resp.status_code == 201, f"Periodo: {periodo_resp.text}"
    periodo_id = periodo_resp.json()["id"]

    turma_resp = await client.post("/api/Turma/", json={
        "codigo_turma": "A_TD", "disciplina_id": disc_id,
        "periodo_letivo_id": periodo_id, "vagas_totais": 40,
        "horario_serializado": "24M34"
    }, headers=headers)
    assert turma_resp.status_code == 201, f"Turma: {turma_resp.text}"
    turma_id = turma_resp.json()["id"]

    docente_resp = await client.post("/api/Docente/", json={
        "matricula": "DOC_TURMA", "nome": "Prof. Teste"
    })
    assert docente_resp.status_code == 201
    docente_id = docente_resp.json()["id"]

    # Vincular docente à turma
    vinculo_resp = await client.post("/api/Docente/turma-docente", json={
        "turma_id": turma_id, "docente_id": docente_id
    })
    assert vinculo_resp.status_code == 201
    vinculo = vinculo_resp.json()
    assert vinculo["turma_id"] == turma_id
    assert vinculo["docente_id"] == docente_id

    # Tentar vincular novamente — deve retornar 409
    vinculo_dup = await client.post("/api/Docente/turma-docente", json={
        "turma_id": turma_id, "docente_id": docente_id
    })
    assert vinculo_dup.status_code == 409

    # Listar docentes da turma
    lista_resp = await client.get(f"/api/Docente/turma/{turma_id}/docentes")
    assert lista_resp.status_code == 200
    assert len(lista_resp.json()) >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# Testes de Relacionamentos (Curso.coordenador, Curso.UO, Disciplina.UO)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_curso_com_coordenador_e_unidade(client, db_session):
    """
    Testa que um Curso pode ser criado com coordenador_id e unidade_organizacional_id,
    conforme as relações do diagrama de entidades.
    """
    headers = await get_auth_headers(client, db_session)

    doc_resp = await client.post("/api/Docente/", json={
        "matricula": "COORD01", "nome": "Prof. Coordenador"
    })
    coordenador_id = doc_resp.json()["id"]

    uo_resp = await client.post("/api/UnidadeOrganizacional/", json={
        "codigo": "CIC_REL", "nome": "Depto. Ciência da Computação"
    })
    uo_id = uo_resp.json()["id"]

    curso_resp = await client.post("/api/Curso/", json={
        "codigo": "CC_REL", "nome": "Ciência da Computação",
        "coordenador_id": coordenador_id,
        "unidade_organizacional_id": uo_id
    }, headers=headers)
    assert curso_resp.status_code == 201, f"Curso: {curso_resp.text}"
    curso = curso_resp.json()
    assert curso["coordenador_id"] == coordenador_id
    assert curso["unidade_organizacional_id"] == uo_id


@pytest.mark.asyncio
async def test_disciplina_com_unidade_organizacional(client, db_session):
    """
    Testa que uma Disciplina pode ser criada com unidade_organizacional_id,
    conforme o diagrama de entidades.
    """
    headers = await get_auth_headers(client, db_session)

    uo_resp = await client.post("/api/UnidadeOrganizacional/", json={
        "codigo": "MAT_REL", "nome": "Depto. Matemática"
    })
    uo_id = uo_resp.json()["id"]

    curso_resp = await client.post("/api/Curso/", json={
        "codigo": "MT_REL", "nome": "Matemática"
    }, headers=headers)
    assert curso_resp.status_code == 201
    curso_id = curso_resp.json()["id"]

    disc_resp = await client.post("/api/Disciplina/", json={
        "codigo": "MAT001_REL", "nome": "Cálculo 1",
        "creditos": 6, "carga_horaria": 90,
        "curso_id": curso_id,
        "unidade_organizacional_id": uo_id
    }, headers=headers)
    assert disc_resp.status_code == 201, f"Disciplina: {disc_resp.text}"
    disc = disc_resp.json()
    assert disc["unidade_organizacional_id"] == uo_id
