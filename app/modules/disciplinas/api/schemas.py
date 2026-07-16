"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Schemas (DTOs) de Disciplina — modelo SIGAA (SIGAA_DISCIPLINA).

Entrada (Create): espelha as colunas físicas, pois é o que se persiste.
Saída: usa os schemas conceituais compartilhados (app/shared/schemas) — a Disciplina
do diagrama, com cargaHorariaTotal derivada e as associações de CargaHoraria
(presencial × EAD) como objetos. Ver docs/mapeamento-conceitual-fisico.md.
"""
from typing import Optional

from pydantic import BaseModel, Field

from app.shared.schemas import Disciplina


class DisciplinaDetalheResponse(Disciplina):
    """Detalhe da disciplina: a entidade conceitual + a auto-associação preRequisito (0..*)."""
    preRequisito: list[Disciplina] = []


class DisciplinaCreate(BaseModel):
    """Schema para criação de uma disciplina (SIGAA_DISCIPLINA)."""
    id: str = Field(..., max_length=7, description="Código da disciplina (ex.: 'CIC0007')")
    nome: Optional[str] = Field(None, max_length=100, description="Nome da disciplina")
    modalidade: Optional[str] = Field(None, max_length=50, description="Modalidade")
    carga_horaria_teorica: Optional[int] = Field(None, ge=0, description="Carga horária teórica")
    carga_horaria_pratica: Optional[int] = Field(None, ge=0, description="Carga horária prática")
    carga_horaria: Optional[int] = Field(None, ge=0, description="Carga horária total da disciplina")
    unidade: str = Field(..., max_length=3, description="Código da unidade organizacional responsável (ex.: 'CIC')")


class PrerequisitoCreate(BaseModel):
    """Schema para vincular um pré-requisito (SIGAA_PREREQ)."""
    disciplina_requerido: str = Field(..., max_length=7, description="Código da disciplina exigida como pré-requisito")
