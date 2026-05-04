"""
Módulo de Serviços (Application Layer) para Currículos.

Contém a lógica de negócio para gerenciamento de Currículos e a associação com
Disciplinas (componentes curriculares). Utiliza SQLAlchemy assíncrono.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from typing import List

from app.modules.curriculos.infrastructure.orm_models import Curriculo, CurriculoDisciplina
from app.modules.curriculos.api.schemas import (
    CurriculoCreate, CurriculoUpdate, CurriculoResponse,
    CurriculoDisciplinaCreate, CurriculoDisciplinaResponse,
    CargaHorariaSchema, PrazoSchema
)
from app.modules.cursos.infrastructure.orm_models import Curso
from app.modules.turmas.infrastructure.orm_models import PeriodoLetivo
from app.modules.disciplinas.infrastructure.orm_models import Disciplina

class CurriculoService:
    """Serviço que abstrai as operações com a entidade Curriculo."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    def _map_to_response(self, curriculo: Curriculo) -> CurriculoResponse:
        """
        Mapeia o modelo ORM achatado (flat) para o schema aninhado (nested) Pydantic.
        """
        return CurriculoResponse(
            id=curriculo.id,
            codigo=curriculo.codigo,
            status=curriculo.status,
            data_validade=curriculo.data_validade,
            curso_id=curriculo.curso_id,
            periodo_letivo_vigor_id=curriculo.periodo_letivo_vigor_id,
            carga_horaria=CargaHorariaSchema(
                total_minima=curriculo.carga_horaria_total_minima,
                obrigatoria_aula=curriculo.carga_horaria_obrigatoria_aula,
                obrigatoria_orientacao=curriculo.carga_horaria_obrigatoria_orientacao,
                obrigatoria_total=curriculo.carga_horaria_obrigatoria_total,
                optativa_minima=curriculo.carga_horaria_optativa_minima,
                maxima_eletivos=curriculo.carga_horaria_maxima_eletivos,
                maxima_periodo=curriculo.carga_horaria_maxima_periodo,
                minima_periodo=curriculo.carga_horaria_minima_periodo
            ),
            prazo=PrazoSchema(
                minimo=curriculo.prazo_minimo,
                medio=curriculo.prazo_medio,
                maximo=curriculo.prazo_maximo
            )
        )

    async def create_curriculo(self, curriculo_in: CurriculoCreate) -> CurriculoResponse:
        """
        Cria um novo currículo, validando a existência do Curso e do Período Letivo.
        """
        # Validar Curso
        curso_result = await self.db.execute(select(Curso).filter(Curso.id == curriculo_in.curso_id))
        if not curso_result.scalars().first():
            raise HTTPException(status_code=404, detail="Curso não encontrado")
            
        # Validar Período Letivo
        periodo_result = await self.db.execute(select(PeriodoLetivo).filter(PeriodoLetivo.id == curriculo_in.periodo_letivo_vigor_id))
        if not periodo_result.scalars().first():
            raise HTTPException(status_code=404, detail="Período Letivo não encontrado")

        # Verifica código duplicado
        codigo_result = await self.db.execute(select(Curriculo).filter(Curriculo.codigo == curriculo_in.codigo))
        if codigo_result.scalars().first():
            raise HTTPException(status_code=400, detail="Código de currículo já existe")

        db_curriculo = Curriculo(
            codigo=curriculo_in.codigo,
            status=curriculo_in.status,
            data_validade=curriculo_in.data_validade,
            curso_id=curriculo_in.curso_id,
            periodo_letivo_vigor_id=curriculo_in.periodo_letivo_vigor_id,
            
            # Carga Horária
            carga_horaria_total_minima=curriculo_in.carga_horaria.total_minima,
            carga_horaria_obrigatoria_aula=curriculo_in.carga_horaria.obrigatoria_aula,
            carga_horaria_obrigatoria_orientacao=curriculo_in.carga_horaria.obrigatoria_orientacao,
            carga_horaria_obrigatoria_total=curriculo_in.carga_horaria.obrigatoria_total,
            carga_horaria_optativa_minima=curriculo_in.carga_horaria.optativa_minima,
            carga_horaria_maxima_eletivos=curriculo_in.carga_horaria.maxima_eletivos,
            carga_horaria_maxima_periodo=curriculo_in.carga_horaria.maxima_periodo,
            carga_horaria_minima_periodo=curriculo_in.carga_horaria.minima_periodo,

            # Prazo
            prazo_minimo=curriculo_in.prazo.minimo,
            prazo_medio=curriculo_in.prazo.medio,
            prazo_maximo=curriculo_in.prazo.maximo
        )
        self.db.add(db_curriculo)
        await self.db.commit()
        await self.db.refresh(db_curriculo)
        return self._map_to_response(db_curriculo)

    async def get_curriculo(self, curriculo_id: int) -> CurriculoResponse:
        """
        Recupera os detalhes de um currículo específico pelo seu ID.
        """
        result = await self.db.execute(select(Curriculo).filter(Curriculo.id == curriculo_id))
        db_curriculo = result.scalars().first()
        if not db_curriculo:
            raise HTTPException(status_code=404, detail="Currículo não encontrado")
        return self._map_to_response(db_curriculo)

    async def list_curriculos(self, skip: int = 0, limit: int = 100) -> List[CurriculoResponse]:
        """
        Lista currículos de forma paginada.
        """
        result = await self.db.execute(select(Curriculo).offset(skip).limit(limit))
        curriculos = result.scalars().all()
        return [self._map_to_response(c) for c in curriculos]

    async def add_disciplina(self, curriculo_id: int, disc_in: CurriculoDisciplinaCreate) -> CurriculoDisciplinaResponse:
        """
        Adiciona uma disciplina a um currículo através da tabela associativa.
        """
        # Validar Currículo
        curr_result = await self.db.execute(select(Curriculo).filter(Curriculo.id == curriculo_id))
        if not curr_result.scalars().first():
            raise HTTPException(status_code=404, detail="Currículo não encontrado")
            
        # Validar Disciplina
        disc_result = await self.db.execute(select(Disciplina).filter(Disciplina.id == disc_in.disciplina_id))
        if not disc_result.scalars().first():
            raise HTTPException(status_code=404, detail="Disciplina não encontrada")

        # Verifica duplicidade
        existe_result = await self.db.execute(select(CurriculoDisciplina).filter(
            CurriculoDisciplina.curriculo_id == curriculo_id,
            CurriculoDisciplina.disciplina_id == disc_in.disciplina_id
        ))
        if existe_result.scalars().first():
            raise HTTPException(status_code=400, detail="Disciplina já vinculada a este currículo")

        assoc = CurriculoDisciplina(
            curriculo_id=curriculo_id,
            disciplina_id=disc_in.disciplina_id,
            tipo=disc_in.tipo,
            nivel=disc_in.nivel
        )
        self.db.add(assoc)
        await self.db.commit()
        await self.db.refresh(assoc)
        return assoc
