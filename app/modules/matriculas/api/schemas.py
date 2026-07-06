"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Schemas (DTOs) de Matrícula — modelo SIGAA.

No SIGAA a matrícula é uma única entidade (SIGAA_MATRICULA) cujo estágio é indicado
pelo código de status (SIGAA_MATRICULA_STATUS): 'PND' (Pedido), 'MAT' (Matriculado),
'NEL' (Não elegível), 'CEX' (Créditos excedidos), 'JMD' (Já matriculado na disciplina),
'CON' (Conflito de horário), 'FUL' (Vagas excedidas), etc. A trilha de auditoria fica
em SIGAA_MATRICULA_HISTORICO.
"""
from typing import Any, Optional

from pydantic import BaseModel, Field


# ── Solicitação/criação de matrícula (status inicial 'PND') ─────────────────────
class MatriculaCreate(BaseModel):
    """Um pedido de matrícula: aluno (matrícula) numa turma."""
    aluno: str = Field(..., max_length=9, description="Matrícula do aluno (ex.: '180012345')")
    turma: int = Field(..., description="ID da turma desejada")
    prioridade: Optional[int] = Field(None, ge=0, description="Prioridade do pedido")


class MatriculaStatusResponse(BaseModel):
    """Resposta resumida de uma matrícula."""
    id: int
    aluno_curso: int
    turma: int
    status: str
    prioridade: Optional[int] = None


# ── Serviço de Tarefa: verificarElegibilidade (§5.2, §7.1) ──────────────────────
class ElegibilidadeRequest(BaseModel):
    """Par (aluno, disciplina) a avaliar."""
    aluno: str = Field(..., max_length=9, description="Matrícula do aluno")
    disciplina: str = Field(..., max_length=7, description="Código da disciplina (ex.: 'CIC0007')")


class ElegibilidadeResponse(BaseModel):
    """Resultado da verificação de elegibilidade (§7.1)."""
    elegivel: bool
    motivos: list[str] = Field(default_factory=list)
    detalhes: dict[str, Any] = Field(default_factory=dict)


# ── Processamento batch (Fases 3 e 5, §7.2–§7.4) ────────────────────────────────
class ProcessamentoRequest(BaseModel):
    """Dispara o processamento batch de um período letivo."""
    periodo_letivo: str = Field(..., max_length=5, description="Período letivo (ex.: '20182')")


class ProcessamentoResponse(BaseModel):
    """Resumo do processamento batch."""
    fase: str
    periodo_letivo: str
    total_pedidos: int = 0
    aprovadas: int = 0
    rejeitadas: int = 0


# ── Matrícula extraordinária (§7.5) ─────────────────────────────────────────────
class ExtraordinariaRequest(BaseModel):
    """Matrícula extraordinária — processamento imediato."""
    aluno: str = Field(..., max_length=9, description="Matrícula do aluno")
    turma: int = Field(..., description="ID da turma desejada")
