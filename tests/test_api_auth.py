"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Módulo: Testes de Autorização e Contratos (RBAC)
Descrição: Garante que as rotas expostas pela API estão devidamente protegidas 
pelo RoleChecker (Role-Based Access Control) e validam corretamente os tokens JWT.
Verifica o acesso baseado em perfis como ALUNO, ADMIN, CONSULTA, etc.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.usuarios.infrastructure.orm_models import Usuario, RoleEnum
from app.core.security import get_password_hash

@pytest.mark.asyncio
async def test_rbac_access_control(client: AsyncClient, db_session: AsyncSession):
    """
    Testa a proteção das rotas utilizando o RoleChecker.
    Cria dois usuários com papéis distintos (ALUNO e CONSULTA) e garante que
    apenas o usuário com o perfil exigido consiga acesso aos endpoints sensíveis.
    """
    # Setup test users
    senha_hash = get_password_hash("senha123")
    
    import uuid
    usuario_aluno = Usuario(id=str(uuid.uuid4()), username="aluno_test", hashed_password=senha_hash, role=RoleEnum.ALUNO)
    usuario_consulta = Usuario(id=str(uuid.uuid4()), username="consulta_test", hashed_password=senha_hash, role=RoleEnum.CONSULTA)
    
    db_session.add(usuario_aluno)
    db_session.add(usuario_consulta)
    await db_session.flush()

    # Login as ALUNO
    response_aluno_login = await client.post("/api/v1/auth/login", data={
        "username": "aluno_test",
        "password": "senha123"
    })
    assert response_aluno_login.status_code == 200
    token_aluno = response_aluno_login.json()["access_token"]

    # Login as CONSULTA
    response_consulta_login = await client.post("/api/v1/auth/login", data={
        "username": "consulta_test",
        "password": "senha123"
    })
    assert response_consulta_login.status_code == 200
    token_consulta = response_consulta_login.json()["access_token"]

    # Test RBAC
    # /api/v1/alunos/ requires [ADMIN, COORDENACAO, PROCESSAMENTO, CONSULTA]
    
    # 1. ALUNO tries to access -> should get 403 Forbidden
    response_forbidden = await client.get("/api/v1/alunos/", headers={
        "Authorization": f"Bearer {token_aluno}"
    })
    assert response_forbidden.status_code == 403
    assert response_forbidden.json()["detail"] == "Operação não permitida para o seu perfil"

    # 2. CONSULTA tries to access -> should get 200 OK
    response_ok = await client.get("/api/v1/alunos/", headers={
        "Authorization": f"Bearer {token_consulta}"
    })
    assert response_ok.status_code == 200
