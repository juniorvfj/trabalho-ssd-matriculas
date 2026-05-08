"""
Módulo de Schemas (DTOs) de Histórico Acadêmico

Define os modelos Pydantic para entrada e saída do histórico acadêmico consolidado
(HistoricoAcademico — 1:1 com Aluno) e dos itens individuais de disciplinas
cursadas (HistoricoDisciplina).
"""
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake
from typing import Optional, List
from enum import Enum


class StatusHistoricoAcademicoEnum(str, Enum):
    """Status do histórico acadêmico consolidado do aluno."""
    ATIVO = "ATIVO"
    INATIVO = "INATIVO"
    CONCLUIDO = "CONCLUIDO"


class StatusDisciplinaHistoricoEnum(str, Enum):
    """Status individual de uma disciplina no histórico."""
    APROVADO = "APROVADO"
    REPROVADO = "REPROVADO"
    TRANCADO = "TRANCADO"
    CURSANDO = "CURSANDO"


# ═══════════════════════════════════════════════════════════════════════════════
# Schemas de HistoricoDisciplina (itens individuais)
# ═══════════════════════════════════════════════════════════════════════════════

class HistoricoDisciplinaBase(BaseModel):
    """Atributos compartilhados dos itens de disciplina no histórico."""
    disciplina_id: int = Field(..., description="ID da disciplina cursada")
    periodo_letivo_id: int = Field(..., description="ID do período letivo")
    mencao: Optional[str] = Field(None, max_length=10, description="Menção obtida (ex: SS, MS, MM, MI, II, SR)")
    frequencia: Optional[int] = Field(None, ge=0, le=100, description="Frequência percentual (0 a 100)")
    status: StatusDisciplinaHistoricoEnum = Field(..., description="Status na disciplina (APROVADO, REPROVADO, TRANCADO, CURSANDO)")


class HistoricoDisciplinaCreate(HistoricoDisciplinaBase):
    """Schema para adicionar uma disciplina ao histórico de um aluno."""
    pass


class HistoricoDisciplinaResponse(HistoricoDisciplinaBase):
    """Schema de resposta de um item de disciplina no histórico."""
    id: int
    historico_academico_id: int

    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Schemas de HistoricoAcademico (entidade consolidada 1:1 com Aluno)
# ═══════════════════════════════════════════════════════════════════════════════

class HistoricoAcademicoBase(BaseModel):
    """Atributos compartilhados do histórico acadêmico consolidado."""
    aluno_id: int = Field(..., description="ID do aluno (relação 1:1)")
    carga_horaria_integralizada: int = Field(default=0, ge=0, description="Carga horária já cumprida")
    carga_horaria_pendente: int = Field(default=0, ge=0, description="Carga horária pendente")
    status: StatusHistoricoAcademicoEnum = Field(
        default=StatusHistoricoAcademicoEnum.ATIVO,
        description="Status geral do histórico (ATIVO, INATIVO, CONCLUIDO)"
    )


class HistoricoAcademicoCreate(HistoricoAcademicoBase):
    """Schema para criação do histórico acadêmico consolidado de um aluno."""
    pass


class HistoricoAcademicoResponse(HistoricoAcademicoBase):
    """Schema de resposta do histórico acadêmico consolidado, incluindo disciplinas cursadas."""
    id: int
    disciplinas: List[HistoricoDisciplinaResponse] = Field(default_factory=list, description="Disciplinas cursadas pelo aluno")

    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)
