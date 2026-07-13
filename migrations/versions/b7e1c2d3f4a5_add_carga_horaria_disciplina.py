"""add carga_horaria em sigaa_disciplina

Autores: Vicente Jr., Brenno Ribeiro e Rosane
Disciplina: Segurança em Sistemas Distribuídos — UnB (Prof. Ricardo Puttini)

Migration de exemplo: acrescenta a coluna CARGA_HORARIA (total) à tabela
SIGAA_DISCIPLINA. A coluna é nullable para não conflitar com o DML do professor
(que insere as disciplinas sem informar esse campo).

Revision ID: b7e1c2d3f4a5
Revises: a4cb4bb91965
Create Date: 2026-07-13 20:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7e1c2d3f4a5"
down_revision: Union[str, Sequence[str], None] = "a4cb4bb91965"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona a coluna carga_horaria (nullable) em sigaa_disciplina."""
    op.add_column(
        "sigaa_disciplina",
        sa.Column("carga_horaria", sa.Numeric(precision=4, scale=0), nullable=True),
    )


def downgrade() -> None:
    """Remove a coluna carga_horaria de sigaa_disciplina."""
    op.drop_column("sigaa_disciplina", "carga_horaria")
