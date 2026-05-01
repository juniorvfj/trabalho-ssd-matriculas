import enum
from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    ALUNO = "ALUNO"
    COORDENACAO = "COORDENACAO"
    PROCESSAMENTO = "PROCESSAMENTO"
    CONSULTA = "CONSULTA"

class Usuario(Base):
    """
    Modelo ORM para a entidade Usuario.
    Mapeia a tabela 'usuarios' no banco de dados.
    """
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, username={self.username}, role={self.role})>"
