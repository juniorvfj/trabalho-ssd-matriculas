"""align entities with diagram

Revision ID: b5c6d7e8f9a0
Revises: a1b2c3d4e5f6
Create Date: 2026-05-06 18:57:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5c6d7e8f9a0'
down_revision: Union[str, None] = '48b129c429e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === HISTORICO ACADEMICO — REESTRUTURAÇÃO COMPLETA ===
    
    # 1. Dropar a tabela antiga (tinha modelagem conceitual incorreta)
    op.drop_table('historicos_academicos')
    
    # 2. Criar nova tabela HistoricoAcademico (entidade consolidada 1:1 com Aluno)
    op.create_table('historicos_academicos',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('aluno_id', sa.Integer(), sa.ForeignKey('alunos.id'), nullable=False, unique=True),
        sa.Column('carga_horaria_integralizada', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('carga_horaria_pendente', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.Enum('ATIVO', 'INATIVO', 'CONCLUIDO', name='statushistoricoacademico'), nullable=False, server_default='ATIVO'),
    )
    op.create_index('ix_historicos_academicos_id', 'historicos_academicos', ['id'])
    
    # 3. Criar nova tabela HistoricoDisciplina (itens individuais do histórico)
    op.create_table('historico_disciplinas',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('historico_academico_id', sa.Integer(), sa.ForeignKey('historicos_academicos.id'), nullable=False),
        sa.Column('disciplina_id', sa.Integer(), sa.ForeignKey('disciplinas.id'), nullable=False),
        sa.Column('periodo_letivo_id', sa.Integer(), sa.ForeignKey('periodos_letivos.id'), nullable=False),
        sa.Column('mencao', sa.String(10), nullable=True),
        sa.Column('frequencia', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('APROVADO', 'REPROVADO', 'TRANCADO', 'CURSANDO', name='statusdisciplinahistorico'), nullable=False),
    )
    op.create_index('ix_historico_disciplinas_id', 'historico_disciplinas', ['id'])

    # === CURSO — ADICIONAR CAMPOS DO DIAGRAMA ===
    op.add_column('cursos', sa.Column('turno', sa.String(50), nullable=True))
    op.add_column('cursos', sa.Column('grau', sa.String(50), nullable=True))
    op.add_column('cursos', sa.Column('modalidade', sa.String(50), nullable=True))
    op.add_column('cursos', sa.Column('sede', sa.String(100), nullable=True))

    # === DISCIPLINA — ADICIONAR CAMPOS DO DIAGRAMA ===
    op.add_column('disciplinas', sa.Column('modalidade', sa.String(50), nullable=True))
    op.add_column('disciplinas', sa.Column('carga_horaria_teorica', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('disciplinas', sa.Column('carga_horaria_pratica', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('disciplinas', sa.Column('carga_horaria_extensionista', sa.Integer(), nullable=False, server_default='0'))

    # === TURMA — ADICIONAR CAMPO STATUS ===
    op.add_column('turmas', sa.Column('status', sa.String(30), nullable=False, server_default='ABERTA'))

    # === MATRICULA — ADICIONAR CAMPOS DO DIAGRAMA ===
    op.add_column('matriculas', sa.Column('motivo_indeferimento', sa.String(500), nullable=True))
    op.add_column('matriculas', sa.Column('prioridade', sa.Integer(), nullable=False, server_default='0'))

    # === PERIODO LETIVO — ADICIONAR CAMPOS DO DIAGRAMA ===
    op.add_column('periodos_letivos', sa.Column('ano', sa.Integer(), nullable=True))
    op.add_column('periodos_letivos', sa.Column('periodo', sa.Integer(), nullable=True))


def downgrade() -> None:
    # === PERIODO LETIVO ===
    op.drop_column('periodos_letivos', 'periodo')
    op.drop_column('periodos_letivos', 'ano')

    # === MATRICULA ===
    op.drop_column('matriculas', 'prioridade')
    op.drop_column('matriculas', 'motivo_indeferimento')

    # === TURMA ===
    op.drop_column('turmas', 'status')

    # === DISCIPLINA ===
    op.drop_column('disciplinas', 'carga_horaria_extensionista')
    op.drop_column('disciplinas', 'carga_horaria_pratica')
    op.drop_column('disciplinas', 'carga_horaria_teorica')
    op.drop_column('disciplinas', 'modalidade')

    # === CURSO ===
    op.drop_column('cursos', 'sede')
    op.drop_column('cursos', 'modalidade')
    op.drop_column('cursos', 'grau')
    op.drop_column('cursos', 'turno')

    # === HISTORICO DISCIPLINAS ===
    op.drop_table('historico_disciplinas')

    # === HISTORICO ACADEMICO — RESTAURAR TABELA ANTIGA ===
    op.drop_table('historicos_academicos')
    op.create_table('historicos_academicos',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('aluno_id', sa.Integer(), sa.ForeignKey('alunos.id'), nullable=False),
        sa.Column('disciplina_id', sa.Integer(), sa.ForeignKey('disciplinas.id'), nullable=False),
        sa.Column('periodo_letivo_id', sa.Integer(), sa.ForeignKey('periodos_letivos.id'), nullable=False),
        sa.Column('nota_final', sa.Float(), nullable=True),
        sa.Column('aprovado', sa.Boolean(), nullable=True),
        sa.Column('status', sa.Enum('APROVADO', 'REPROVADO', 'TRANCADO', 'CURSANDO', name='statushistorico'), nullable=False),
    )
    op.create_index('ix_historicos_academicos_id', 'historicos_academicos', ['id'])
