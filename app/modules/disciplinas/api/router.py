"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Rotas (API Layer) de Disciplina — modelo SIGAA (SIGAA_DISCIPLINA).

A pesquisa devolve {id, nome, unidade}; o detalhe inclui as cargas horárias
(teórica, prática e total) e a lista de pré-requisitos, seguindo as consultas
do arquivo de referência SIGAA-API.sql.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.shared.responses import SearchSet, search_set
from .schemas import DisciplinaCreate, DisciplinaResponse, PrerequisitoCreate
from ..application.services import (
    add_prerequisito,
    create_disciplina,
    get_disciplina_by_id,
    get_prerequisitos,
    search_disciplinas,
)

router = APIRouter(tags=["Disciplina"])


def _int(v) -> Optional[int]:
    return int(v) if v is not None else None


@router.get("/", response_model=SearchSet, summary="Pesquisar disciplinas")
async def get_all_disciplinas(
    db: AsyncSession = Depends(get_db),
    nome: Optional[str] = Query(None, description="Filtro por nome (parcial)"),
    modalidade: Optional[str] = Query(None, description="Filtro por modalidade"),
    unidade: Optional[str] = Query(None, description="Filtro por código de unidade organizacional"),
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset"),
):
    """Pesquisa disciplinas por nome/modalidade/unidade (SearchSet)."""
    disciplinas, total = await search_disciplinas(db, nome, modalidade, unidade, _offset, _count)
    items = [
        {
            "resourceType": "Disciplina",
            "id": d.id,
            "nome": d.nome,
            "unidade": {"resourceType": "UnidadeOrganizacional", "id": d.unidade},
        }
        for d in disciplinas
    ]
    extra = ""
    if nome:
        extra += f"nome={nome}&"
    if modalidade:
        extra += f"modalidade={modalidade}&"
    if unidade:
        extra += f"unidade={unidade}&"
    return search_set(items, total, _offset, _count, "/api/Disciplina", extra)


@router.post("/", response_model=DisciplinaResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar disciplina")
async def post_disciplina(disciplina: DisciplinaCreate, db: AsyncSession = Depends(get_db)):
    """Cria uma nova disciplina (SIGAA_DISCIPLINA)."""
    return await create_disciplina(db, disciplina)


@router.get("/{id}", summary="Buscar disciplina por código")
async def get_disciplina(id: str, db: AsyncSession = Depends(get_db)):
    """Retorna os detalhes de uma disciplina, cargas horárias e pré-requisitos."""
    d = await get_disciplina_by_id(db, id)
    prereqs = await get_prerequisitos(db, id)
    teorica = _int(d.carga_horaria_teorica) or 0
    pratica = _int(d.carga_horaria_pratica) or 0
    # Usa a carga horária total informada (coluna nova); se ausente, soma teórica + prática.
    carga_total = _int(d.carga_horaria)
    if carga_total is None:
        carga_total = teorica + pratica
    return {
        "resourceType": "Disciplina",
        "id": d.id,
        "nome": d.nome,
        "modalidade": d.modalidade,
        "cargaHorariaTeorica": teorica,
        "cargaHorariaPratica": pratica,
        "cargaHoraria": _int(d.carga_horaria),
        "cargaHorariaTotal": carga_total,
        "unidade": {"resourceType": "UnidadeOrganizacional", "id": d.unidade},
        "prerequisitos": [
            {"resourceType": "Disciplina", "id": p.id, "nome": p.nome, "unidade": p.unidade}
            for p in prereqs
        ],
    }


@router.post("/{id}/prerequisitos", status_code=status.HTTP_201_CREATED, summary="Vincular pré-requisito")
async def post_prerequisito(id: str, prereq: PrerequisitoCreate, db: AsyncSession = Depends(get_db)):
    """Vincula uma disciplina como pré-requisito da disciplina informada (SIGAA_PREREQ)."""
    await add_prerequisito(db, id, prereq)
    return {
        "resourceType": "Prerequisito",
        "disciplinaRequer": id,
        "disciplinaRequerido": prereq.disciplina_requerido,
    }
