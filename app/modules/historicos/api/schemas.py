"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Schemas (DTOs) de Histórico Acadêmico — modelo SIGAA.

No banco não há entidade "histórico consolidado": o HistoricoAcademico conceitual é
derivado das linhas de SIGAA_RL_ALUNO_CURSO_DISCIPLINA + o vínculo SIGAA_RL_ALUNO_CURSO.
A resposta segue o HistoricoAcademico.yml do professor: cargas horárias consolidadas
derivadas e disciplinas como Disciplina_HistoricoAcademico (herança de Disciplina).
"""
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.shared.schemas import AlunoShort, DisciplinaHistoricoAcademico, Resource


class HistoricoAcademicoResponse(Resource):
    """HistoricoAcademico conceitual (id = matrícula do aluno) — mapeamento, Seção 4.3."""
    resourceType: str = "HistoricoAcademico"
    cargaHorariaIntegralizadas: Optional[int] = Field(
        None, description="Derivado: Σ carga horária das disciplinas com menção de aprovação"
    )
    cargaHorariaPendente: Optional[int] = Field(
        None, description="Derivado: mínimo total do currículo − carga integralizada"
    )
    status: Optional[str] = Field(None, description="'ativo'/'inativo'/'concluido' ← STATUS do vínculo")
    aluno: Optional[AlunoShort] = None
    disciplina: list[DisciplinaHistoricoAcademico] = []


class HistoricoDisciplinaCreate(BaseModel):
    """Schema para lançar uma disciplina cursada no histórico de um vínculo aluno-curso."""
    aluno_curso: int = Field(..., description="ID do vínculo aluno-curso (SIGAA_RL_ALUNO_CURSO.id)")
    disciplina: str = Field(..., max_length=7, description="Código da disciplina cursada")
    periodo_letivo: str = Field(..., max_length=5, description="Período letivo (ex.: '20182')")
    mencao: Optional[str] = Field(None, max_length=2, description="Menção obtida (ex.: 'SS', 'MM', 'SR')")


class HistoricoDisciplinaResponse(BaseModel):
    """Schema de resposta de um item do histórico."""
    aluno_curso: int
    disciplina: str
    periodo_letivo: str
    mencao: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
