"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Rotas (API Layer) de Unidade Organizacional — modelo SIGAA (SIGAA_UNIDADE).
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.shared.responses import SearchSet, search_set
from app.modules.unidades_organizacionais.api.schemas import (
    UnidadeOrganizacionalCreate,
    UnidadeOrganizacionalResponse,
)
from app.modules.unidades_organizacionais.application.services import (
    create_unidade,
    get_unidade_by_id,
    search_unidades,
)

router = APIRouter(tags=["Unidade Organizacional"])


def _to_item(u) -> dict:
    return {"resourceType": "UnidadeOrganizacional", "id": u.id, "nome": u.nome}


@router.get("/", response_model=SearchSet, summary="Pesquisar unidades organizacionais")
async def list_unidades(
    db: AsyncSession = Depends(get_db),
    nome: Optional[str] = Query(None, description="Filtro por nome (parcial)"),
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset"),
):
    """Pesquisa unidades organizacionais (departamentos, institutos, faculdades)."""
    unidades, total = await search_unidades(db, nome, _offset, _count)
    extra = f"nome={nome}&" if nome else ""
    return search_set([_to_item(u) for u in unidades], total, _offset, _count, "/api/UnidadeOrganizacional", extra)


@router.post("/", response_model=UnidadeOrganizacionalResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar unidade organizacional")
async def create_new_unidade(unidade_in: UnidadeOrganizacionalCreate, db: AsyncSession = Depends(get_db)):
    """Cadastra uma nova unidade organizacional."""
    return await create_unidade(db, unidade_in)


@router.get("/{unidade_id}", summary="Buscar unidade organizacional por código")
async def get_unidade(unidade_id: str, db: AsyncSession = Depends(get_db)):
    """Retorna os dados de uma unidade organizacional pelo seu código (ex.: 'CIC')."""
    u = await get_unidade_by_id(db, unidade_id)
    return _to_item(u)
