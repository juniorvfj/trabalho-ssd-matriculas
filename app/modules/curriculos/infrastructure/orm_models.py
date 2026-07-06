"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Módulo de Modelos ORM (Infrastructure Layer) — Currículo (Estrutura Curricular)

Mapeia as tabelas SIGAA_CURRICULO, SIGAA_RL_CURRICULO_CURSO e
SIGAA_RL_CURRICULO_DISCIPLINA do modelo do professor. O currículo usa como PK o
código natural de 7 caracteres (ex.: '6351/2'). O período letivo de vigor é um
'character varying(5)' inline (ex.: '20182'), como no schema SIGAA.
"""
from sqlalchemy import Column, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Curriculo(Base):
    """Entidade que mapeia a tabela SIGAA_CURRICULO (estrutura curricular)."""
    __tablename__ = "sigaa_curriculo"

    # Código natural do currículo (PK) — ex.: '6351/2'
    id = Column(String(7), primary_key=True)
    status = Column(String(1), nullable=True)  # ex.: 'A' (ativo)
    periodo_letivo_vigor = Column(String(5), nullable=False)  # ex.: '20182'

    carga_horaria_minima_total = Column(Numeric(5, 0), nullable=False)
    carga_horaria_minima_opt = Column(Numeric(5, 0), nullable=False)
    carga_horaria_obr = Column(Numeric(5, 0), nullable=False)
    carga_horaria_eletiva_max = Column(Numeric(5, 0), nullable=False)
    carga_horaria_max_periodo = Column(Numeric(5, 0), nullable=False)
    num_periodos = Column(Numeric(2, 0), nullable=False)
    min_periodos = Column(Numeric(2, 0), nullable=False)
    max_periodos = Column(Numeric(2, 0), nullable=False)

    # --- Relacionamentos ORM ---
    cursos = relationship("CurriculoCurso", back_populates="curriculo_rel")
    disciplinas = relationship("CurriculoDisciplina", back_populates="curriculo_rel")


class CurriculoCurso(Base):
    """Tabela associativa SIGAA_RL_CURRICULO_CURSO (M:N Currículo ↔ Curso)."""
    __tablename__ = "sigaa_rl_curriculo_curso"

    curriculo = Column(String(7), ForeignKey("sigaa_curriculo.id"), primary_key=True)
    curso = Column(String(4), ForeignKey("sigaa_curso.id"), primary_key=True)

    curriculo_rel = relationship("Curriculo", back_populates="cursos")
    curso_rel = relationship("Curso")


class CurriculoDisciplina(Base):
    """
    Tabela associativa SIGAA_RL_CURRICULO_DISCIPLINA: componentes curriculares.
    'periodo' é o nível/semestre sugerido; 'tipo' é 'OBR' (obrigatória) ou 'OPT' (optativa).
    """
    __tablename__ = "sigaa_rl_curriculo_disciplina"

    curriculo = Column(String(7), ForeignKey("sigaa_curriculo.id"), primary_key=True)
    disciplina = Column(String(7), ForeignKey("sigaa_disciplina.id"), primary_key=True)
    periodo = Column(Numeric(2, 0), nullable=True)
    tipo = Column(String(15), nullable=False)  # 'OBR' | 'OPT'

    curriculo_rel = relationship("Curriculo", back_populates="disciplinas")
    disciplina_rel = relationship("Disciplina")
