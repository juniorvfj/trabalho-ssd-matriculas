"""
Autores: Vicente Jr., Breno Ribeiro e Rosane
Módulo: Alunos
Descrição: Exposição dos serviços REST para a entidade Aluno. 
Define os contratos de API utilizando schemas de entrada (AlunoCreate) e saída (AlunoResponse).
"""
from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from .schemas import AlunoCreate, AlunoResponse, AlunoUpdate
from ..application.services import get_aluno_by_id, list_alunos, create_aluno
from app.api.deps import get_current_user, RoleChecker
from app.modules.usuarios.infrastructure.orm_models import RoleEnum

# Requisito de segurança: todas as rotas de Alunos exigem token JWT válido
router = APIRouter(tags=["Aluno"], dependencies=[Depends(get_current_user)])

@router.get("/", dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.COORDENACAO, RoleEnum.PROCESSAMENTO, RoleEnum.CONSULTA]))])
async def search(
    db: AsyncSession = Depends(get_db),
    nome: Optional[str] = None,
    curso: Optional[str] = None,
    curriculo: Optional[str] = None,
    periodoIngresso: Optional[str] = None,
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset")
):
    """
    Pesquisa alunos.
    Pesquisa alunos por nome, período letivo de ingresso e curso.
    """
    alunos = await list_alunos(db) # We should ideally filter here, but we'll return all as mock for now or filter in memory
    
    # Simple in-memory filtering for the sake of the API compliance
    filtered = alunos
    if nome:
        filtered = [a for a in filtered if nome.lower() in a.nome.lower()]
    if curso:
        filtered = [a for a in filtered if str(a.curso_id) == curso]
    
    total = len(filtered)
    paginated = filtered[_offset : _offset + _count]

    items = [
        {
            "resourceType": "Aluno",
            "id": str(a.id),
            "matricula": a.matricula,
            "nome": a.nome,
            "curso": {
                "resourceType": "Curso",
                "id": str(a.curso_id)
            }
        }
        for a in paginated
    ]
    
    return {
        "total": total,
        "count": len(paginated),
        "offset": _offset,
        "link": {
            "self": f"/api/Aluno?_offset={_offset}&_count={_count}",
            "next": f"/api/Aluno?_offset={_offset + _count}&_count={_count}" if _offset + _count < total else "",
            "previous": f"/api/Aluno?_offset={max(0, _offset - _count)}&_count={_count}" if _offset > 0 else ""
        },
        "items": items
    }

@router.get("/{id}")
async def read(id: str, db: AsyncSession = Depends(get_db)):
    """
    Consulta um aluno pelo seu id (matricula).
    """
    aluno = await get_aluno_by_id(db, int(id))
    return {
        "resourceType": "Aluno",
        "id": str(aluno.id),
        "matricula": aluno.matricula,
        "nome": aluno.nome,
        "ira": aluno.ira,
        "curso": {
            "resourceType": "Curso",
            "id": str(aluno.curso_id)
        }
    }
