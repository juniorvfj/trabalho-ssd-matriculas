"""
Módulo de Schemas (DTOs) de Matrículas

Utiliza o Pydantic para definir Data Transfer Objects (DTOs) das entidades
SolicitacaoMatricula, Matricula e AuditoriaProcessamento, além dos schemas
do serviço de tarefa verificarElegibilidade (§5.2).

Estes schemas garantem que os dados de entrada e saída da API estejam corretos
antes de atingirem a lógica de negócio ou o banco de dados.
"""
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_snake
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════════
# Enums Pydantic — espelham os Enums do ORM para validação na camada de API
# ═══════════════════════════════════════════════════════════════════════════════

class StatusSolicitacaoEnum(str, Enum):
    """Enum espelhado no Pydantic para validação de status da solicitação."""
    PENDENTE = "PENDENTE"
    APROVADA = "APROVADA"
    REJEITADA = "REJEITADA"


class StatusMatriculaEnum(str, Enum):
    """Enum espelhado no Pydantic para validação de status da matrícula."""
    ATIVA = "ATIVA"
    CANCELADA = "CANCELADA"
    TRANCADA = "TRANCADA"


# ═══════════════════════════════════════════════════════════════════════════════
# Schemas de SolicitacaoMatricula
# ═══════════════════════════════════════════════════════════════════════════════

class SolicitacaoMatriculaBase(BaseModel):
    """Atributos compartilhados entre criação e resposta de Solicitação de Matrícula."""
    aluno_id: int = Field(..., gt=0, description="ID do aluno que solicita a matrícula")
    turma_id: int = Field(..., gt=0, description="ID da turma desejada")
    prioridade: int = Field(default=0, ge=0, description="Prioridade da solicitação (0 = mais alta)")
    fase: str = Field(default="FASE_3", max_length=30, description="Fase do processamento (FASE_3, FASE_5, EXTRAORDINARIA)")


class SolicitacaoMatriculaCreate(SolicitacaoMatriculaBase):
    """Schema específico para criação de uma solicitação de matrícula via POST."""
    pass


class SolicitacaoMatriculaResponse(SolicitacaoMatriculaBase):
    """Schema de resposta, incluindo ID, status e timestamp gerados pelo sistema."""
    id: int
    status: StatusSolicitacaoEnum = Field(..., description="Estado atual da solicitação no pipeline")
    resultado: Optional[str] = Field(None, description="Motivo da rejeição (quando aplicável)")
    timestamp_solicitacao: datetime = Field(..., description="Data/hora da solicitação")

    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Schemas de Matricula
# ═══════════════════════════════════════════════════════════════════════════════

class MatriculaBase(BaseModel):
    """Atributos compartilhados entre criação e resposta de Matrícula."""
    aluno_id: int = Field(..., gt=0, description="ID do aluno matriculado")
    turma_id: int = Field(..., gt=0, description="ID da turma")
    periodo_letivo_id: int = Field(..., gt=0, description="ID do período letivo")
    origem: str = Field(default="FASE_3", max_length=30, description="Origem da matrícula (FASE_3, EXTRAORDINARIA, REMATRICULA)")


class MatriculaCreate(MatriculaBase):
    """Schema específico para criação de uma matrícula via POST."""
    pass


class MatriculaResponse(MatriculaBase):
    """Schema de resposta, incluindo ID, status e data de efetivação gerados pelo sistema."""
    id: int
    status: StatusMatriculaEnum = Field(..., description="Estado atual da matrícula")
    data_efetivacao: datetime = Field(..., description="Data em que a matrícula foi efetivada")

    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Schemas de AuditoriaProcessamento
# ═══════════════════════════════════════════════════════════════════════════════

class AuditoriaProcessamentoResponse(BaseModel):
    """
    Schema de resposta para registros de auditoria do processamento batch.
    Somente leitura — os registros são criados internamente pelo motor de processamento.
    """
    id: int
    aluno_id: int = Field(..., description="ID do aluno avaliado")
    turma_id: int = Field(..., description="ID da turma avaliada")
    fase: str = Field(..., description="Fase do processamento (FASE_3, FASE_5)")
    regra_aplicada: str = Field(..., description="Regra que foi avaliada (R1_ELEGIBILIDADE, R2_ORDENACAO, etc.)")
    decisao: str = Field(..., description="Resultado: APROVADO ou REJEITADO")
    mensagem: str = Field(..., description="Mensagem descritiva da decisão")
    timestamp_evento: datetime = Field(..., description="Data/hora da avaliação")

    model_config = ConfigDict(from_attributes=True, alias_generator=to_snake, populate_by_name=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Schemas do Serviço de Tarefa — verificarElegibilidade (§5.2, §7.1)
# ═══════════════════════════════════════════════════════════════════════════════

class ElegibilidadeRequest(BaseModel):
    """
    Schema de entrada para o serviço de tarefa verificarElegibilidade.
    Recebe o par (aluno, disciplina) a ser avaliado.
    """
    aluno_id: int = Field(..., gt=0, description="ID do aluno a ser verificado")
    disciplina_id: int = Field(..., gt=0, description="ID da disciplina pretendida")


class ElegibilidadeResponse(BaseModel):
    """
    Schema de resposta do serviço de tarefa verificarElegibilidade (§7.1).

    Retorna se o aluno é elegível para cursar a disciplina e, em caso negativo,
    lista os motivos de impedimento e detalhes adicionais para rastreabilidade.
    """
    elegivel: bool = Field(..., description="Indica se o aluno é elegível para a disciplina")
    motivos: List[str] = Field(default_factory=list, description="Lista de motivos de impedimento (vazia se elegível)")
    detalhes: Dict[str, Any] = Field(default_factory=dict, description="Informações adicionais para depuração")


# ═══════════════════════════════════════════════════════════════════════════════
# Schemas do Processamento Batch — Fases 3 e 5 (§7.2–§7.4)
# ═══════════════════════════════════════════════════════════════════════════════

class ProcessamentoRequest(BaseModel):
    """Schema de entrada para disparar o processamento batch de um período letivo."""
    periodo_letivo_id: int = Field(..., gt=0, description="ID do período letivo a processar")


class ProcessamentoResponse(BaseModel):
    """
    Resumo do resultado do processamento batch.
    Inclui contadores de solicitações processadas, aprovadas e rejeitadas.
    """
    fase: str = Field(..., description="Fase processada (FASE_3, FASE_5)")
    periodo_letivo_id: int = Field(..., description="ID do período letivo processado")
    total_solicitacoes: int = Field(default=0, description="Total de solicitações avaliadas")
    aprovadas: int = Field(default=0, description="Quantidade de matrículas efetivadas")
    rejeitadas: int = Field(default=0, description="Quantidade de solicitações rejeitadas")


# ═══════════════════════════════════════════════════════════════════════════════
# Schemas da Matrícula Extraordinária (§7.5)
# ═══════════════════════════════════════════════════════════════════════════════

class ExtraordinariaRequest(BaseModel):
    """Schema de entrada para matrícula extraordinária — processamento imediato."""
    aluno_id: int = Field(..., gt=0, description="ID do aluno solicitante")
    turma_id: int = Field(..., gt=0, description="ID da turma desejada")


# ═══════════════════════════════════════════════════════════════════════════════
# Schema do Comprovante de Matrícula
# ═══════════════════════════════════════════════════════════════════════════════

class ComprovanteMatriculaItem(BaseModel):
    """Representa uma disciplina/turma no comprovante de matrícula do aluno."""
    matricula_id: int = Field(..., description="ID da matrícula")
    disciplina_nome: str = Field(..., description="Nome da disciplina")
    turma_codigo: str = Field(..., description="Código da turma (ex: A, T01)")
    horario: str = Field(..., description="Horário serializado")
    creditos: int = Field(..., description="Créditos da disciplina")
    status: str = Field(..., description="Status da matrícula (ATIVA, CANCELADA, TRANCADA)")


class ComprovanteMatriculaResponse(BaseModel):
    """
    Comprovante de matrícula completo do aluno para o período vigente.
    Lista todas as disciplinas/turmas em que o aluno está matriculado.
    """
    aluno_id: int = Field(..., description="ID do aluno")
    aluno_nome: str = Field(..., description="Nome do aluno")
    aluno_matricula: str = Field(..., description="Número de matrícula")
    periodo_letivo_id: int = Field(..., description="ID do período letivo")
    total_creditos: int = Field(default=0, description="Total de créditos matriculados")
    disciplinas: List[ComprovanteMatriculaItem] = Field(default_factory=list, description="Lista de disciplinas matriculadas")
