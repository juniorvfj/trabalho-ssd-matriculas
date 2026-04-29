"""Add solicitacoes_matricula, matriculas and auditoria_processamento tables

Revision ID: a1b2c3d4e5f6
Revises: 004401650ca4
Create Date: 2026-04-29 18:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '004401650ca4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema — cria as 3 tabelas do módulo de Matrículas."""

    # Tabela de Solicitações de Matrícula (§6.10)
    op.create_table('solicitacoes_matricula',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('aluno_id', sa.Integer(), nullable=False),
        sa.Column('turma_id', sa.Integer(), nullable=False),
        sa.Column('prioridade', sa.Integer(), nullable=False),
        sa.Column('fase', sa.String(length=30), nullable=False),
        sa.Column('status', sa.Enum('PENDENTE', 'APROVADA', 'REJEITADA', name='statussolicitacao'), nullable=False),
        sa.Column('resultado', sa.String(length=500), nullable=True),
        sa.Column('timestamp_solicitacao', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['aluno_id'], ['alunos.id'], ),
        sa.ForeignKeyConstraint(['turma_id'], ['turmas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_solicitacoes_matricula_id'), 'solicitacoes_matricula', ['id'], unique=False)

    # Tabela de Matrículas Efetivadas (§6.11)
    op.create_table('matriculas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('aluno_id', sa.Integer(), nullable=False),
        sa.Column('turma_id', sa.Integer(), nullable=False),
        sa.Column('periodo_letivo_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('ATIVA', 'CANCELADA', 'TRANCADA', name='statusmatricula'), nullable=False),
        sa.Column('origem', sa.String(length=30), nullable=False),
        sa.Column('data_efetivacao', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['aluno_id'], ['alunos.id'], ),
        sa.ForeignKeyConstraint(['turma_id'], ['turmas.id'], ),
        sa.ForeignKeyConstraint(['periodo_letivo_id'], ['periodos_letivos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_matriculas_id'), 'matriculas', ['id'], unique=False)

    # Tabela de Auditoria do Processamento (§6.12)
    op.create_table('auditoria_processamento',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('aluno_id', sa.Integer(), nullable=False),
        sa.Column('turma_id', sa.Integer(), nullable=False),
        sa.Column('fase', sa.String(length=30), nullable=False),
        sa.Column('regra_aplicada', sa.String(length=50), nullable=False),
        sa.Column('decisao', sa.String(length=20), nullable=False),
        sa.Column('mensagem', sa.String(length=500), nullable=False),
        sa.Column('timestamp_evento', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['aluno_id'], ['alunos.id'], ),
        sa.ForeignKeyConstraint(['turma_id'], ['turmas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auditoria_processamento_id'), 'auditoria_processamento', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema — remove as 3 tabelas do módulo de Matrículas."""
    op.drop_index(op.f('ix_auditoria_processamento_id'), table_name='auditoria_processamento')
    op.drop_table('auditoria_processamento')
    op.drop_index(op.f('ix_matriculas_id'), table_name='matriculas')
    op.drop_table('matriculas')
    op.drop_index(op.f('ix_solicitacoes_matricula_id'), table_name='solicitacoes_matricula')
    op.drop_table('solicitacoes_matricula')
