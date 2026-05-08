"""
Módulo de Unidades Organizacionais — Serviço de Entidade.

Representa os departamentos, institutos e faculdades da universidade.
Conforme o diagrama de entidades:
  - Curso → unidadeOrganizacional (0..1) — Um curso pertence a uma UO
  - Disciplina → unidadeOrganizacional (0..1) — Uma disciplina pode pertencer a uma UO

Estrutura interna:
  - api/router.py           → Endpoints REST: GET/POST /unidades-organizacionais
  - api/schemas.py          → DTOs Pydantic (UnidadeOrganizacionalCreate, UnidadeOrganizacionalResponse)
  - application/services.py → Lógica de negócio: CRUD com validação de código duplicado
  - infrastructure/orm_models.py → Modelo ORM: UnidadeOrganizacional com relacionamentos bidirecionais
"""
