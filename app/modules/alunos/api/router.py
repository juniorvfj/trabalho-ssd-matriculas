"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Rotas (API Layer) de Aluno — modelo SIGAA (SIGAA_ALUNO + SIGAA_RL_ALUNO_CURSO).

A pesquisa devolve {matricula, nome}; o detalhe inclui curso, currículo, IRA e o
período de ingresso (ano/número), seguindo a consulta do arquivo SIGAA-API.sql.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.shared.responses import SearchSet, search_set
from app.shared.schemas import PeriodoLetivo
from .schemas import AlunoCreate, AlunoResponse
from ..application.services import (
    create_aluno,
    get_aluno_by_matricula,
    get_vinculo_com_curso,
    search_alunos,
)

router = APIRouter(tags=["Aluno"])


@router.get("/", response_model=SearchSet, summary="Pesquisar alunos")
async def search(
    db: AsyncSession = Depends(get_db),
    nome: Optional[str] = Query(None, description="Filtro por nome (parcial)"),
    curso: Optional[str] = Query(None, description="Filtro por código de curso"),
    periodoIngresso: Optional[str] = Query(None, description="Filtro por período de ingresso (ex.: '20182')"),
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset"),
):
    """Pesquisa alunos por nome, curso e/ou período de ingresso (SearchSet)."""
    alunos, total = await search_alunos(db, nome, curso, periodoIngresso, _offset, _count)
    items = [{"resourceType": "Aluno", "matricula": a.matricula, "nome": a.nome} for a in alunos]
    extra = ""
    if nome:
        extra += f"nome={nome}&"
    if curso:
        extra += f"curso={curso}&"
    if periodoIngresso:
        extra += f"periodoIngresso={periodoIngresso}&"
    return search_set(items, total, _offset, _count, "/api/Aluno", extra)


@router.post("/", response_model=AlunoResponse, status_code=status.HTTP_201_CREATED, summary="Cadastrar aluno")
async def create(aluno_in: AlunoCreate, db: AsyncSession = Depends(get_db)):
    """Cadastra um aluno e seu vínculo de curso (SIGAA_ALUNO + SIGAA_RL_ALUNO_CURSO)."""
    return await create_aluno(db, aluno_in)


@router.get("/{id}", summary="Buscar aluno por matrícula")
async def read(id: str, db: AsyncSession = Depends(get_db)):
    """Retorna os dados do aluno, seu curso, currículo, IRA e período de ingresso."""
    aluno = await get_aluno_by_matricula(db, id)
    vinculo = await get_vinculo_com_curso(db, id)

    resposta: dict = {
        "resourceType": "Aluno",
        "id": aluno.matricula,
        "matricula": aluno.matricula,
        "nome": aluno.nome,
    }
    if vinculo:
        ac, curso = vinculo
        # Formato do Aluno.yml do professor: periodoIngresso como PeriodoLetivo {ano, periodo}
        # e curriculo como Curriculo_Short (id na convenção pública '6351.2').
        periodo = PeriodoLetivo.from_sigaa(ac.periodo_letivo_registro)
        curriculo_id = (ac.curriculo or "").replace("/", ".")
        resposta.update(
            {
                "curso": {"resourceType": "Curso", "id": curso.id, "codigo": curso.id, "nome": curso.nome},
                "curriculo": {"resourceType": "Curriculo", "id": curriculo_id, "codigo": curriculo_id},
                "ira": ac.ira,
                "periodoIngresso": periodo.model_dump() if periodo else None,
            }
        )
    return resposta
