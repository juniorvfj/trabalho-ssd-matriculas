"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Rotas (API Layer) de Curso — modelo SIGAA (SIGAA_CURSO).

A pesquisa (GET /) devolve o envelope SearchSet com {id, nome}; o detalhe (GET /{id})
inclui grau/turno/modalidade/coordenador e a lista de unidades organizacionais,
seguindo as consultas do arquivo de referência SIGAA-API.sql.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.shared.responses import SearchSet, search_set
from .schemas import CursoCreate, CursoResponse
from ..application.services import (
    create_curso,
    get_curso_by_id,
    get_unidades_do_curso,
    search_cursos,
)

router = APIRouter(tags=["Curso"])


@router.get("/", response_model=SearchSet, summary="Pesquisar cursos")
async def get_all_cursos(
    db: AsyncSession = Depends(get_db),
    nome: Optional[str] = Query(None, description="Filtro por nome (parcial)"),
    unidade: Optional[str] = Query(None, description="Filtro por código de unidade organizacional"),
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset"),
):
    """Pesquisa cursos por nome e/ou unidade organizacional (SearchSet)."""
    cursos, total = await search_cursos(db, nome, unidade, _offset, _count)
    items = [{"resourceType": "Curso", "id": c.id, "nome": c.nome} for c in cursos]
    extra = ""
    if nome:
        extra += f"nome={nome}&"
    if unidade:
        extra += f"unidade={unidade}&"
    return search_set(items, total, _offset, _count, "/api/Curso", extra)


@router.post("/", response_model=CursoResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar curso")
async def post_curso(curso: CursoCreate, db: AsyncSession = Depends(get_db)):
    """Cadastra um novo curso (SIGAA_CURSO)."""
    return await create_curso(db, curso)


@router.get("/{id}", summary="Buscar curso por código")
async def get_curso(id: str, db: AsyncSession = Depends(get_db)):
    """Retorna os detalhes de um curso e suas unidades organizacionais."""
    c = await get_curso_by_id(db, id)
    unidades = await get_unidades_do_curso(db, id)
    return {
        "resourceType": "Curso",
        "id": c.id,
        "nome": c.nome,
        "grauAcademico": c.grau_academico,
        "turno": c.turno,
        "modalidade": c.modalidade,
        "coordenador": c.coordenador,
        "unidades": [
            {"resourceType": "UnidadeOrganizacional", "id": u.id, "nome": u.nome} for u in unidades
        ],
    }
