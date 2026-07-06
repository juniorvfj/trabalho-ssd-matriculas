"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Módulo de Modelos ORM (Infrastructure Layer) — Unidade Organizacional

Mapeia a tabela SIGAA_UNIDADE do modelo de dados de referência do professor
(departamentos, institutos e faculdades). A chave primária é o código natural
de 3 caracteres (ex.: 'CIC', 'ENE'), exatamente como no schema SIGAA.
"""
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class UnidadeOrganizacional(Base):
    """Entidade que mapeia a tabela SIGAA_UNIDADE (unidade acadêmica responsável)."""
    __tablename__ = "sigaa_unidade"

    # Código natural da unidade (PK) — ex.: 'CIC', 'ENE', 'MAT'
    id = Column(String(3), primary_key=True)
    nome = Column(String(100), nullable=False)

    # Disciplinas oferecidas por esta unidade
    disciplinas = relationship("Disciplina", back_populates="unidade_organizacional")
