"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Módulo de Modelos ORM (Infrastructure Layer) — Histórico Acadêmico

Mapeia a tabela SIGAA_RL_ALUNO_CURSO_DISCIPLINA do modelo do professor: cada
registro é uma disciplina cursada por um vínculo aluno-curso, num dado período
letivo, com a menção obtida. É a base usada pela verificação de elegibilidade
(uma disciplina é considerada cumprida quando a menção é de aprovação).

Observação: no schema SIGAA não existe uma tabela consolidada de "histórico
acadêmico" (visão 1:1 com o aluno); o histórico É o conjunto de linhas desta
tabela associativa.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class HistoricoDisciplina(Base):
    """
    Tabela SIGAA_RL_ALUNO_CURSO_DISCIPLINA: disciplina cursada por um vínculo
    aluno-curso, com a menção obtida no período letivo informado.
    """
    __tablename__ = "sigaa_rl_aluno_curso_disciplina"

    aluno_curso = Column(Integer, ForeignKey("sigaa_rl_aluno_curso.id"), primary_key=True)
    disciplina = Column(String(7), ForeignKey("sigaa_disciplina.id"), primary_key=True)
    periodo_letivo = Column(String(5), primary_key=True)  # ex.: '20182'
    mencao = Column(String(2), nullable=True)  # ex.: 'SS', 'MM', 'MI', 'SR'

    # --- Relacionamentos ORM ---
    vinculo = relationship("AlunoCurso")
    disciplina_rel = relationship("Disciplina")
