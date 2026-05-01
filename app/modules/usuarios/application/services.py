from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.modules.usuarios.infrastructure.orm_models import Usuario
from app.modules.usuarios.schemas import UsuarioCreate
from app.core.security import get_password_hash

class UsuarioService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> Optional[Usuario]:
        """Busca um usuário pelo username."""
        result = await self.db.execute(select(Usuario).filter(Usuario.username == username))
        return result.scalars().first()

    async def get_by_id(self, user_id: str) -> Optional[Usuario]:
        """Busca um usuário pelo ID."""
        result = await self.db.execute(select(Usuario).filter(Usuario.id == user_id))
        return result.scalars().first()

    async def create(self, obj_in: UsuarioCreate) -> Usuario:
        """Cria um novo usuário com senha em hash."""
        db_obj = Usuario(
            id=obj_in.id,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            role=obj_in.role,
            is_active=obj_in.is_active
        )
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj
