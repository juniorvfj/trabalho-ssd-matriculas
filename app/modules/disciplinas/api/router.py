"""
Autores: Vicente Jr., Breno Ribeiro e Rosane
Módulo: Disciplinas
Descrição: Gerencia os endpoints das disciplinas, incluindo a definição
de pré-requisitos, créditos e carga horária.
"""
from fastapi import APIRouter, Depends, status, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user

from .schemas import DisciplinaCreate, DisciplinaResponse, DisciplinaUpdate
from ..application.services import get_disciplina_by_id, list_disciplinas, create_disciplina

router = APIRouter(tags=["Disciplinas"], dependencies=[Depends(get_current_user)])

@router.get("/")
async def get_all_disciplinas(
    db: AsyncSession = Depends(get_db),
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset")
):
    """
    Retorna a lista completa de disciplinas cadastradas na base.
    """
    disciplinas = await list_disciplinas(db)
    
    total = len(disciplinas)
    paginated = disciplinas[_offset : _offset + _count]

    items = [
        {
            "resourceType": "Disciplina",
            "id": str(d.id),
            "codigo": d.codigo,
            "nome": d.nome,
            "modalidade": d.modalidade,
            "creditos": d.creditos,
            "cargaHoraria": d.carga_horaria,
            "curso": {
                "resourceType": "Curso",
                "id": str(d.curso_id)
            },
            "unidadeOrganizacional": {
                "resourceType": "UnidadeOrganizacional",
                "id": str(d.unidade_organizacional_id)
            } if d.unidade_organizacional_id else None,
            "ativa": d.ativa
        }
        for d in paginated
    ]
    
    return {
        "total": total,
        "count": len(paginated),
        "offset": _offset,
        "link": {
            "self": f"/api/Disciplina?_offset={_offset}&_count={_count}",
            "next": f"/api/Disciplina?_offset={_offset + _count}&_count={_count}" if _offset + _count < total else "",
            "previous": f"/api/Disciplina?_offset={max(0, _offset - _count)}&_count={_count}" if _offset > 0 else ""
        },
        "items": items
    }

@router.post("/", response_model=DisciplinaResponse, status_code=status.HTTP_201_CREATED)
async def post_disciplina(disciplina: DisciplinaCreate, db: AsyncSession = Depends(get_db)):
    """
    Cria uma nova disciplina. 
    Lança erro caso o ID do curso vinculado seja inválido ou código já exista.
    """
    return await create_disciplina(db, disciplina)

@router.get("/{id}")
async def get_disciplina(id: int, db: AsyncSession = Depends(get_db)):
    """
    Recupera as informações detalhadas de uma disciplina pelo seu ID.
    """
    d = await get_disciplina_by_id(db, id)
    return {
        "resourceType": "Disciplina",
        "id": str(d.id),
        "codigo": d.codigo,
        "nome": d.nome,
        "modalidade": d.modalidade,
        "creditos": d.creditos,
        "cargaHoraria": d.carga_horaria,
        "curso": {
            "resourceType": "Curso",
            "id": str(d.curso_id)
        },
        "unidadeOrganizacional": {
            "resourceType": "UnidadeOrganizacional",
            "id": str(d.unidade_organizacional_id)
        } if d.unidade_organizacional_id else None,
        "ativa": d.ativa
    }
