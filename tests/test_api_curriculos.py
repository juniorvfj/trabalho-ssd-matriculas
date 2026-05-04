"""
Módulo de Testes para o Serviço de Currículos (API e Aplicação).

Verifica o correto funcionamento do CRUD de currículos e da adição 
de disciplinas, além de testar as validações de banco de dados.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.modules.usuarios.infrastructure.orm_models import Usuario, RoleEnum
from app.core.security import get_password_hash
from app.modules.cursos.infrastructure.orm_models import Curso
from app.modules.turmas.infrastructure.orm_models import PeriodoLetivo
from app.modules.disciplinas.infrastructure.orm_models import Disciplina

@pytest.mark.asyncio
async def test_curriculo_crud(client: AsyncClient, db_session: AsyncSession):
    """
    Testa o fluxo completo (CRUD) de um currículo via API.
    """
    # 1. Setup inicial de dados auxiliares no BD
    # 1.1 Criar Usuário Admin
    senha_hash = get_password_hash("senha123")
    usuario_admin = Usuario(
        id=str(uuid.uuid4()), 
        username="admin_curriculo", 
        hashed_password=senha_hash, 
        role=RoleEnum.ADMIN
    )
    db_session.add(usuario_admin)

    # 1.2 Criar Curso
    curso_test = Curso(codigo="CUR01", nome="Curso Teste")
    db_session.add(curso_test)
    
    # 1.3 Criar Período Letivo
    from datetime import date
    periodo_test = PeriodoLetivo(
        codigo="2026.1", 
        descricao="Semestre 1 2026", 
        data_inicio=date(2026, 3, 1), 
        data_fim=date(2026, 7, 30)
    )
    db_session.add(periodo_test)
    
    # 1.4 Criar Disciplina para o teste de associação
    disciplina_test = Disciplina(
        codigo="DISC01", 
        nome="Disciplina Teste", 
        creditos=4, 
        carga_horaria=60, 
        curso_id=1 # Será ajustado via flush
    )
    db_session.add(disciplina_test)
    
    await db_session.flush()
    # Atribuir curso_id correto à disciplina
    disciplina_test.curso_id = curso_test.id
    await db_session.flush()

    # 2. Login para obter o token JWT
    resp_login = await client.post("/api/v1/auth/login", data={
        "username": "admin_curriculo",
        "password": "senha123"
    })
    assert resp_login.status_code == 200
    token = resp_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Teste de Criação (POST /api/v1/curriculos)
    curriculo_data = {
        "codigo": "CURRICULO_2026",
        "status": "ativo",
        "data_validade": "2030-12-31",
        "curso_id": curso_test.id,
        "periodo_letivo_vigor_id": periodo_test.id,
        "carga_horaria": {
            "total_minima": 3600,
            "obrigatoria_aula": 2400,
            "obrigatoria_orientacao": 100,
            "obrigatoria_total": 2500,
            "optativa_minima": 1100,
            "maxima_eletivos": 400,
            "maxima_periodo": 460,
            "minima_periodo": 200
        },
        "prazo": {
            "minimo": 8,
            "medio": 10,
            "maximo": 14
        }
    }
    
    resp_create = await client.post("/api/v1/curriculos/", json=curriculo_data, headers=headers)
    assert resp_create.status_code == 201
    created_curriculo = resp_create.json()
    assert created_curriculo["codigo"] == "CURRICULO_2026"
    assert created_curriculo["carga_horaria"]["total_minima"] == 3600
    curriculo_id = created_curriculo["id"]

    # 4. Teste de Leitura Unica (GET /api/v1/curriculos/{id})
    resp_get = await client.get(f"/api/v1/curriculos/{curriculo_id}", headers=headers)
    assert resp_get.status_code == 200
    assert resp_get.json()["codigo"] == "CURRICULO_2026"

    # 5. Teste de Associação de Disciplina (POST /api/v1/curriculos/{id}/disciplinas)
    assoc_data = {
        "disciplina_id": disciplina_test.id,
        "tipo": "Obrigatória",
        "nivel": 1
    }
    resp_assoc = await client.post(f"/api/v1/curriculos/{curriculo_id}/disciplinas", json=assoc_data, headers=headers)
    assert resp_assoc.status_code == 201
    assert resp_assoc.json()["tipo"] == "Obrigatória"
    
    # Tentar associar novamente deve falhar com 400
    resp_assoc_fail = await client.post(f"/api/v1/curriculos/{curriculo_id}/disciplinas", json=assoc_data, headers=headers)
    assert resp_assoc_fail.status_code == 400
