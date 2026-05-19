"""
Autores: Vicente Jr., Breno Ribeiro e Rosane
Módulo: Cursos
Descrição: Define as rotas (endpoints REST) da entidade Curso, aplicando
as regras de contratos (Schemas Pydantic) para garantir validação de entrada/saída.
"""
from fastapi import APIRouter, Depends, status, Query
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from .schemas import CursoCreate, CursoResponse, CursoUpdate
from ..application.services import get_curso_by_id, list_cursos, create_curso
from app.api.deps import get_current_user

# Define o agrupador de rotas e impõe o requisito de autenticação (get_current_user)
router = APIRouter(tags=["Cursos"], dependencies=[Depends(get_current_user)])

@router.get("/")
async def get_all_cursos(
    db: AsyncSession = Depends(get_db),
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset")
):
    """
    Lista todos os cursos disponíveis.
    Retorna uma lista padronizada paginada (SearchSet).
    """
    cursos = await list_cursos(db)
    
    total = len(cursos)
    paginated = cursos[_offset : _offset + _count]

    items = [
        {
            "resourceType": "Curso",
            "id": str(c.id),
            "codigo": c.codigo,
            "nome": c.nome,
            "turno": c.turno,
            "grau": c.grau,
            "modalidade": c.modalidade,
            "sede": c.sede,
            "coordenador": {
                "resourceType": "Docente",
                "id": str(c.coordenador_id)
            } if c.coordenador_id else None,
            "unidadeOrganizacional": {
                "resourceType": "UnidadeOrganizacional",
                "id": str(c.unidade_organizacional_id)
            } if c.unidade_organizacional_id else None,
            "ativo": c.ativo
        }
        for c in paginated
    ]
    
    return {
        "total": total,
        "count": len(paginated),
        "offset": _offset,
        "link": {
            "self": f"/api/Curso?_offset={_offset}&_count={_count}",
            "next": f"/api/Curso?_offset={_offset + _count}&_count={_count}" if _offset + _count < total else "",
            "previous": f"/api/Curso?_offset={max(0, _offset - _count)}&_count={_count}" if _offset > 0 else ""
        },
        "items": items
    }

@router.post("/", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
async def post_curso(curso: CursoCreate, db: AsyncSession = Depends(get_db)):
    """
    Cadastra um novo curso.
    Valida a carga útil da requisição pelo esquema CursoCreate.
    Retorna status 201 (Created) se houver sucesso.
    """
    return await create_curso(db, curso)

@router.get("/{id}")
async def get_curso(id: int, db: AsyncSession = Depends(get_db)):
    """
    Busca os detalhes de um curso específico pelo seu ID.
    Lança erro 404 (Not Found) se o curso não for encontrado na base.
    """
    c = await get_curso_by_id(db, id)
    return {
        "resourceType": "Curso",
        "id": str(c.id),
        "codigo": c.codigo,
        "nome": c.nome,
        "turno": c.turno,
        "grau": c.grau,
        "modalidade": c.modalidade,
        "sede": c.sede,
        "coordenador": {
            "resourceType": "Docente",
            "id": str(c.coordenador_id)
        } if c.coordenador_id else None,
        "unidadeOrganizacional": {
            "resourceType": "UnidadeOrganizacional",
            "id": str(c.unidade_organizacional_id)
        } if c.unidade_organizacional_id else None,
        "ativo": c.ativo
    }
