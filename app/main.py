"""
Autores: Vicente Jr., Breno Ribeiro e Rosane
Disciplina: Segurança em Sistemas Distribuídos
Prof: Ricardo Staciarini Puttini

Este é o arquivo principal de inicialização da API (Entrypoint).
Utilizamos o FastAPI para expor os serviços seguindo a arquitetura
de Monólito Modular (orientação a serviços, estilo RESTful).
"""
from fastapi import FastAPI
from app.core.config import settings

def get_application() -> FastAPI:
    # Instancia o FastAPI e configura a interface de documentação automática (Swagger UI)
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        description="API para o Sistema de Matrícula de Alunos de Graduação (Trabalho SSD)",
        contact={
            "name": "Vicente Jr. (juniorvf@gmail.com / vicente.junior@aluno.unb.br)",
            "email": "juniorvf@gmail.com",
        },
        license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
    )

    from app.api.auth import auth_router
    from app.modules.cursos.api.router import router as cursos_router
    from app.modules.alunos.api.router import router as alunos_router
    from app.core.exceptions import BaseAPIException, api_exception_handler
    from fastapi.exceptions import RequestValidationError
    from app.core.exceptions import validation_exception_handler

    # Registro de Handlers de Exceção para padronizar os erros retornados (Modelos Canônicos de Erro)
    app.add_exception_handler(BaseAPIException, api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Inclusão dos roteadores de cada módulo, separando os contratos de serviço
    app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
    app.include_router(cursos_router, prefix=f"{settings.API_V1_STR}/cursos")
    app.include_router(alunos_router, prefix=f"{settings.API_V1_STR}/alunos")

    from app.modules.disciplinas.api.router import router as disciplinas_router
    from app.modules.turmas.api.router import router as turmas_router
    from app.modules.historicos.api.router import router as historicos_router
    from app.modules.matriculas.api.router import router as matriculas_router
    from app.modules.matriculas.api.router import tarefas_router
    app.include_router(disciplinas_router, prefix=f"{settings.API_V1_STR}/disciplinas")
    app.include_router(turmas_router, prefix=f"{settings.API_V1_STR}/turmas")
    app.include_router(historicos_router, prefix=f"{settings.API_V1_STR}/historicos")

    # Módulo de Matrículas — serviço de entidade (CRUD) e solicitações
    app.include_router(matriculas_router, prefix=f"{settings.API_V1_STR}/matriculas")

    # Serviço de Tarefa — verificarElegibilidade (§5.2) separado em rota própria
    app.include_router(tarefas_router, prefix=f"{settings.API_V1_STR}/tarefas")

    # Endpoint de healthcheck para monitoramento da disponibilidade da API
    @app.get("/health", tags=["System"])
    async def health_check():
        """Verifica se o serviço está operante."""
        return {"status": "ok", "app": settings.PROJECT_NAME}

    # Redirecionamento da raiz da aplicação para a documentação interativa
    @app.get("/", include_in_schema=False)
    async def root():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/docs")

    return app

app = get_application()
