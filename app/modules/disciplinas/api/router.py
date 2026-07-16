"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Rotas (API Layer) de Disciplina — modelo SIGAA (SIGAA_DISCIPLINA).

Os retornos seguem o modelo conceitual do diagrama (app/shared/schemas):
cargaHorariaTotal derivada (teórica + prática, como no SIGAA-API.sql) e as duas
associações de CargaHoraria (presencial × EAD) como objetos. O de-para com as
colunas físicas está em docs/mapeamento-conceitual-fisico.md.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.shared.responses import SearchSet, search_set
from app.shared.schemas import Disciplina, disciplina_para_conceitual
from .schemas import DisciplinaCreate, DisciplinaDetalheResponse, PrerequisitoCreate
from ..application.services import (
    add_prerequisito,
    create_disciplina,
    get_disciplina_com_unidade,
    get_prerequisitos,
    search_disciplinas,
)

router = APIRouter(tags=["Disciplina"])


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
    # Itens resumidos, como na consulta de pesquisa do SIGAA-API.sql (id, nome, unidade)
    items = [
        {
            "resourceType": "Disciplina",
            "id": d.id,
            "codigo": d.id,
            "nome": d.nome,
            "unidadeOrganizacional": {"resourceType": "UnidadeOrganizacional", "id": d.unidade},
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


@router.post("/", response_model=Disciplina, status_code=status.HTTP_201_CREATED, summary="Cadastrar disciplina")
async def post_disciplina(disciplina: DisciplinaCreate, db: AsyncSession = Depends(get_db)):
    """Cria uma nova disciplina (SIGAA_DISCIPLINA); devolve a representação conceitual."""
    d = await create_disciplina(db, disciplina)
    return Disciplina(**disciplina_para_conceitual(d))


@router.get("/{id}", response_model=DisciplinaDetalheResponse, summary="Buscar disciplina por código")
async def get_disciplina(id: str, db: AsyncSession = Depends(get_db)):
    """Retorna a disciplina no modelo conceitual: cargas horárias como objetos e pré-requisitos."""
    d, unidade_nome = await get_disciplina_com_unidade(db, id)
    prereqs = await get_prerequisitos(db, id)
    return DisciplinaDetalheResponse(
        **disciplina_para_conceitual(d, unidade_nome),
        preRequisito=[Disciplina(**disciplina_para_conceitual(p)) for p in prereqs],
    )


@router.post("/{id}/prerequisitos", status_code=status.HTTP_201_CREATED, summary="Vincular pré-requisito")
async def post_prerequisito(id: str, prereq: PrerequisitoCreate, db: AsyncSession = Depends(get_db)):
    """Vincula uma disciplina como pré-requisito da disciplina informada (SIGAA_PREREQ)."""
    await add_prerequisito(db, id, prereq)
    return {
        "resourceType": "Prerequisito",
        "disciplinaRequer": id,
        "disciplinaRequerido": prereq.disciplina_requerido,
    }
