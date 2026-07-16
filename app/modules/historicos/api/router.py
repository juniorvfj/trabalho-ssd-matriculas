"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Rotas (API Layer) de Histórico Acadêmico — modelo SIGAA.

Segue o contrato de referência HistoricoAcademico.yml do professor: GET /{id} devolve o
HistoricoAcademico conceitual (cargas consolidadas derivadas + Aluno_Short) e as
disciplinas cursadas como Disciplina_HistoricoAcademico — herança de Disciplina, com
menção, frequência, status derivado e periodoLetivo como objeto.
De-para: docs/mapeamento-conceitual-fisico.md (Seções 3.2 e 4.3).
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.shared.schemas import (
    STATUS_VINCULO_ALUNO,
    AlunoShort,
    CursoShort,
    DisciplinaHistoricoAcademico,
    PeriodoLetivo,
    disciplina_para_conceitual,
    status_disciplina_cursada,
    _int,
)
from ..api.schemas import (
    HistoricoAcademicoResponse,
    HistoricoDisciplinaCreate,
    HistoricoDisciplinaResponse,
)
from ..application.services import (
    add_disciplina_ao_historico,
    get_aluno_com_vinculo,
    get_historico_by_aluno,
)

router = APIRouter(tags=["HistoricoAcademico"])


def _norm_periodo(periodo: Optional[str]) -> Optional[str]:
    """Aceita o formato do professor ('2018-2') e o armazenado ('20182')."""
    return periodo.replace("-", "") if periodo else None


def _disciplina_cursada(hd, disc) -> DisciplinaHistoricoAcademico:
    """Linha do histórico → Disciplina_HistoricoAcademico (herda a Disciplina conceitual)."""
    return DisciplinaHistoricoAcademico(
        **disciplina_para_conceitual(disc),
        mencao=hd.mencao,
        status=status_disciplina_cursada(hd.mencao),
        periodoLetivo=PeriodoLetivo.from_sigaa(hd.periodo_letivo),
    )


@router.get("/{id}", response_model=HistoricoAcademicoResponse, summary="Histórico do aluno")
async def read(id: str, db: AsyncSession = Depends(get_db)):
    """
    Retorna o HistoricoAcademico conceitual do aluno.

    Os campos consolidados são derivados (não há tabela de histórico no SIGAA):
    cargaHorariaIntegralizadas = Σ das cargas das disciplinas aprovadas;
    cargaHorariaPendente = mínimo total do currículo do vínculo − integralizadas;
    status = STATUS do vínculo aluno-curso ('A' → ativo...).
    """
    aluno, vinculo, curso, curriculo = await get_aluno_com_vinculo(db, id)
    linhas = await get_historico_by_aluno(db, id)
    itens = [_disciplina_cursada(hd, disc) for hd, disc in linhas]

    integralizadas = sum(
        i.cargaHorariaTotal or 0 for i in itens if i.status == "aprovado"
    )
    pendente = None
    if curriculo is not None:
        minima_total = _int(curriculo.carga_horaria_minima_total) or 0
        pendente = max(minima_total - integralizadas, 0)

    return HistoricoAcademicoResponse(
        id=id,
        cargaHorariaIntegralizadas=integralizadas,
        cargaHorariaPendente=pendente,
        status=STATUS_VINCULO_ALUNO.get(vinculo.status, vinculo.status) if vinculo else None,
        aluno=AlunoShort(
            id=aluno.matricula,
            matricula=aluno.matricula,
            nome=aluno.nome,
            curso=CursoShort(id=curso.id, codigo=curso.id, nome=curso.nome) if curso else None,
        ),
        disciplina=itens,
    )


@router.get(
    "/{id}/disciplina",
    response_model=list[DisciplinaHistoricoAcademico],
    summary="Pesquisar disciplinas no histórico",
)
async def search_disciplina(
    id: str,
    db: AsyncSession = Depends(get_db),
    periodoLetivo: Optional[str] = Query(None, description="Filtro por período letivo (ex.: '2018-2')"),
    status_: Optional[str] = Query(
        None,
        alias="status",
        description="Filtro por status derivado (aprovado/reprovado/cursando); aceita lista separada por vírgula",
    ),
    disciplina: Optional[str] = Query(
        None, description="Filtro por código de disciplina; aceita lista separada por vírgula"
    ),
):
    """
    Pesquisa disciplinas do histórico. Retorna um array de Disciplina_HistoricoAcademico,
    como no contrato HistoricoAcademico.yml do professor.
    """
    await get_aluno_com_vinculo(db, id)
    linhas = await get_historico_by_aluno(db, id, _norm_periodo(periodoLetivo))
    itens = [_disciplina_cursada(hd, disc) for hd, disc in linhas]
    if disciplina:
        codigos = {c.strip() for c in disciplina.split(",")}
        itens = [i for i in itens if i.id in codigos]
    if status_:
        alvo = {s.strip() for s in status_.split(",")}
        itens = [i for i in itens if i.status in alvo]
    return itens


@router.post("/disciplina", response_model=HistoricoDisciplinaResponse, status_code=status.HTTP_201_CREATED, summary="Lançar disciplina no histórico")
async def post_disciplina(historico_in: HistoricoDisciplinaCreate, db: AsyncSession = Depends(get_db)):
    """Lança uma disciplina cursada no histórico (SIGAA_RL_ALUNO_CURSO_DISCIPLINA)."""
    return await add_disciplina_ao_historico(db, historico_in)
