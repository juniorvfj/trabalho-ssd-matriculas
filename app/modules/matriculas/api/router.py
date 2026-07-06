"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Rotas (API Layer) de Matrícula — modelo SIGAA.

Serviço de entidade (SIGAA_MATRICULA) com criação em lote (status 'PND'), pesquisa,
detalhe e alteração de status (PATCH/JSON Patch). Inclui o serviço de tarefa
verificarElegibilidade (§5.2), o processamento batch (Fases 3 e 5), a matrícula
extraordinária (§7.5) e os endpoints de comprovante e auditoria.
"""
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.shared.responses import search_set
from .schemas import (
    ElegibilidadeRequest,
    ElegibilidadeResponse,
    ExtraordinariaRequest,
    MatriculaCreate,
    ProcessamentoRequest,
    ProcessamentoResponse,
)
from ..application.elegibilidade import verificar_elegibilidade
from ..application.extraordinaria import processar_extraordinaria
from ..application.processamento import processar_fase
from ..application.services import (
    alterar_status,
    comprovante_matricula,
    create_matriculas,
    get_matricula_by_id,
    historico_processamento,
    search_matriculas,
)

router = APIRouter(tags=["Matrícula"])
tarefas_router = APIRouter(tags=["Serviço de Tarefa"])


def _item(m) -> dict:
    return {
        "resourceType": "Matricula",
        "id": str(m.id),
        "alunoCurso": m.aluno_curso,
        "turma": {"resourceType": "Turma", "id": str(m.turma)},
        "status": m.status,
        "prioridade": int(m.prioridade) if m.prioridade is not None else None,
    }


# ── Serviço de entidade: SIGAA_MATRICULA ────────────────────────────────────────
@router.get("/", summary="Pesquisar matrículas")
async def search(
    periodoLetivo: str = Query(..., description="Período letivo (obrigatório, ex.: '20182')"),
    aluno: Optional[str] = Query(None, description="Matrícula do aluno"),
    turma: Optional[int] = Query(None, description="ID da turma"),
    status_: Optional[str] = Query(None, alias="status", description="Código de status (ex.: 'MAT')"),
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset"),
    db: AsyncSession = Depends(get_db),
):
    """Pesquisa matrículas de um período letivo; ao menos aluno ou turma deve ser informado."""
    if not aluno and not turma:
        raise HTTPException(status_code=400, detail="Informe pelo menos 'aluno' ou 'turma'.")
    matriculas, total = await search_matriculas(db, periodoLetivo, aluno, turma, status_, _offset, _count)
    extra = f"periodoLetivo={periodoLetivo}&"
    if aluno:
        extra += f"aluno={aluno}&"
    if turma:
        extra += f"turma={turma}&"
    return search_set([_item(m) for m in matriculas], total, _offset, _count, "/api/Matricula", extra)


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Criar pedidos de matrícula (lote)")
async def create(pedidos: list[MatriculaCreate], db: AsyncSession = Depends(get_db)):
    """Cria um lote de pedidos de matrícula (status 'PND')."""
    criadas = await create_matriculas(db, pedidos)
    return [_item(m) for m in criadas]


@router.get("/{id}", summary="Buscar matrícula por ID")
async def read(id: int, db: AsyncSession = Depends(get_db)):
    """Retorna os dados de uma matrícula pelo ID."""
    return _item(await get_matricula_by_id(db, id))


@router.patch("/{id}", summary="Alterar status da matrícula (JSON Patch)")
async def patch(id: int, patch_ops: list[dict[str, Any]] = Body(...), db: AsyncSession = Depends(get_db)):
    """
    Altera o status de uma matrícula via JSON Patch. Ex.:
    `[{"op": "replace", "path": "/status", "value": "REA"}]`
    """
    novo_status = None
    for op in patch_ops:
        if op.get("path") == "/status":
            novo_status = op.get("value")
        else:
            raise HTTPException(status_code=400, detail=f"Campo {op.get('path')} não pode ser alterado.")
    if not novo_status:
        raise HTTPException(status_code=400, detail="Operação de status ausente.")
    return _item(await alterar_status(db, id, novo_status))


# ── Serviço de Tarefa: verificarElegibilidade (§5.2, §7.1) ──────────────────────
@tarefas_router.post("/verificar-elegibilidade", response_model=ElegibilidadeResponse, summary="Verificar elegibilidade")
async def post_verificar_elegibilidade(request: ElegibilidadeRequest, db: AsyncSession = Depends(get_db)):
    """Avalia se um aluno pode cursar uma disciplina (§7.1)."""
    return await verificar_elegibilidade(db, request.aluno, request.disciplina)


# ── Processamento batch (Fases 3 e 5, §7.2–§7.4) ────────────────────────────────
@router.post("/processamento/fase-3", response_model=ProcessamentoResponse, summary="Processamento batch (Fase 3)")
async def post_processamento_fase_3(request: ProcessamentoRequest, db: AsyncSession = Depends(get_db)):
    """Dispara o processamento batch da Fase 3 para um período letivo."""
    return await processar_fase(db, request.periodo_letivo, "FASE_3")


@router.post("/processamento/fase-5", response_model=ProcessamentoResponse, summary="Reprocessamento batch (Fase 5)")
async def post_processamento_fase_5(request: ProcessamentoRequest, db: AsyncSession = Depends(get_db)):
    """Dispara o reprocessamento da Fase 5 para um período letivo."""
    return await processar_fase(db, request.periodo_letivo, "FASE_5")


# ── Matrícula extraordinária (§7.5) ─────────────────────────────────────────────
@router.post("/extraordinaria", summary="Matrícula extraordinária")
async def post_extraordinaria(request: ExtraordinariaRequest, db: AsyncSession = Depends(get_db)):
    """Processa uma matrícula extraordinária de forma imediata (§7.5)."""
    return await processar_extraordinaria(db, request.aluno, request.turma)


# ── Comprovante e auditoria ─────────────────────────────────────────────────────
@router.get("/alunos/{aluno}/comprovante-matricula", summary="Comprovante de matrícula")
async def get_comprovante(aluno: str, periodoLetivo: str = Query(...), db: AsyncSession = Depends(get_db)):
    """Gera o comprovante de matrícula do aluno para um período letivo."""
    return await comprovante_matricula(db, aluno, periodoLetivo)


@router.get("/alunos/{aluno}/historico-processamento", summary="Histórico de processamento")
async def get_historico_processamento(aluno: str, db: AsyncSession = Depends(get_db)):
    """Retorna a trilha de auditoria do processamento de matrículas de um aluno."""
    registros = await historico_processamento(db, aluno)
    items = [
        {
            "resourceType": "MatriculaHistorico",
            "id": str(r.id),
            "alunoCurso": r.aluno_curso,
            "status": r.status,
            "turma": r.turma,
            "prioridade": int(r.prioridade) if r.prioridade is not None else None,
            "dataHora": r.data_hora.isoformat() if r.data_hora else None,
        }
        for r in registros
    ]
    return search_set(items, len(items), 0, len(items) or 1, f"/api/Matricula/alunos/{aluno}/historico-processamento")
