"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Schemas (DTOs) de Currículo (Estrutura Curricular) — modelo SIGAA.

Entrada (Create): espelha as colunas físicas de SIGAA_CURRICULO.
Saída: modelo conceitual do diagrama — 'cargaHoraria' e 'prazo' como objetos
(CargaHoraria/Prazo) e 'periodoLetivoVigor' como PeriodoLetivo, derivados das
colunas planas. Ver docs/mapeamento-conceitual-fisico.md (Seções 2.3, 2.4 e 4.2).
"""
from typing import Optional

from pydantic import BaseModel, Field

from app.shared.schemas import CargaHorariaCurriculo, CursoShort, PeriodoLetivo, Prazo, Resource


class CurriculoCreate(BaseModel):
    """Schema para criação de um currículo (SIGAA_CURRICULO)."""
    id: str = Field(..., max_length=7, description="Código do currículo (ex.: '6351/2')")
    status: Optional[str] = Field("A", max_length=1, description="Status (ex.: 'A')")
    periodo_letivo_vigor: str = Field(..., max_length=5, description="Período de vigor (ex.: '20182')")
    carga_horaria_minima_total: int = Field(..., ge=0)
    carga_horaria_minima_opt: int = Field(..., ge=0)
    carga_horaria_obr: int = Field(..., ge=0)
    carga_horaria_eletiva_max: int = Field(..., ge=0)
    carga_horaria_max_periodo: int = Field(..., ge=0)
    num_periodos: int = Field(..., ge=0)
    min_periodos: int = Field(..., ge=0)
    max_periodos: int = Field(..., ge=0)
    curso: Optional[str] = Field(None, max_length=4, description="Curso a vincular (SIGAA_RL_CURRICULO_CURSO)")


class CurriculoResponse(Resource):
    """Currículo no modelo conceitual (cargaHoraria e prazo como objetos de valor)."""
    resourceType: str = "Curriculo"
    codigo: Optional[str] = None
    status: Optional[str] = Field(None, description="Domínio conceitual: 'ativo'/'inativo' ← STATUS 'A'/'I'")
    periodoLetivoVigor: Optional[PeriodoLetivo] = None
    cargaHoraria: Optional[CargaHorariaCurriculo] = None
    prazo: Optional[Prazo] = None
    curso: Optional[CursoShort] = None


class CurriculoDisciplinaCreate(BaseModel):
    """Schema para vincular uma disciplina ao currículo (SIGAA_RL_CURRICULO_DISCIPLINA)."""
    disciplina: str = Field(..., max_length=7, description="Código da disciplina (ex.: 'CIC0007')")
    periodo: Optional[int] = Field(None, ge=0, description="Nível/semestre sugerido")
    tipo: str = Field(..., max_length=15, description="'OBR' (obrigatória) ou 'OPT' (optativa)")
