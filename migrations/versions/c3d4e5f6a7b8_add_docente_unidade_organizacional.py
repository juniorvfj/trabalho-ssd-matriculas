"""add docente, unidade_organizacional e relacoes

Revision ID: c3d4e5f6a7b8
Revises: b5c6d7e8f9a0
Create Date: 2026-05-07 21:58:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b5c6d7e8f9a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === DOCENTE — Nova entidade ===
    op.create_table('docentes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('matricula', sa.String(20), nullable=False, unique=True),
        sa.Column('nome', sa.String(150), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default='true'),
    )
    op.create_index('ix_docentes_id', 'docentes', ['id'])
    op.create_index('ix_docentes_matricula', 'docentes', ['matricula'], unique=True)

    # === UNIDADE ORGANIZACIONAL — Nova entidade ===
    op.create_table('unidades_organizacionais',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('codigo', sa.String(20), nullable=False, unique=True),
        sa.Column('nome', sa.String(150), nullable=False),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default='true'),
    )
    op.create_index('ix_unidades_organizacionais_id', 'unidades_organizacionais', ['id'])
    op.create_index('ix_unidades_organizacionais_codigo', 'unidades_organizacionais', ['codigo'], unique=True)

    # === TURMA_DOCENTES — Tabela associativa N:M ===
    op.create_table('turma_docentes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('turma_id', sa.Integer(), sa.ForeignKey('turmas.id'), nullable=False),
        sa.Column('docente_id', sa.Integer(), sa.ForeignKey('docentes.id'), nullable=False),
    )
    op.create_index('ix_turma_docentes_id', 'turma_docentes', ['id'])

    # === CURSO — Adicionar FKs para coordenador e unidade organizacional ===
    op.add_column('cursos', sa.Column('coordenador_id', sa.Integer(), sa.ForeignKey('docentes.id'), nullable=True))
    op.add_column('cursos', sa.Column('unidade_organizacional_id', sa.Integer(), sa.ForeignKey('unidades_organizacionais.id'), nullable=True))

    # === DISCIPLINA — Adicionar FK para unidade organizacional ===
    op.add_column('disciplinas', sa.Column('unidade_organizacional_id', sa.Integer(), sa.ForeignKey('unidades_organizacionais.id'), nullable=True))


def downgrade() -> None:
    # === DISCIPLINA ===
    op.drop_column('disciplinas', 'unidade_organizacional_id')

    # === CURSO ===
    op.drop_column('cursos', 'unidade_organizacional_id')
    op.drop_column('cursos', 'coordenador_id')

    # === TURMA_DOCENTES ===
    op.drop_table('turma_docentes')

    # === UNIDADE ORGANIZACIONAL ===
    op.drop_table('unidades_organizacionais')

    # === DOCENTE ===
    op.drop_table('docentes')
