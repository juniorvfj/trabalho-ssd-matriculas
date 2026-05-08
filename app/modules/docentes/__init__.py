"""
Módulo de Docentes — Serviço de Entidade (§6.7 do enunciado).

Representa o corpo docente da universidade. Cada docente pode atuar como:
  - Coordenador de um Curso (relação 0..1 via FK coordenador_id em cursos)
  - Professor de uma ou mais Turmas (relação N:M via tabela turma_docentes)

Estrutura interna:
  - api/router.py           → Endpoints REST: GET/POST /docentes, vinculação turma-docente
  - api/schemas.py          → DTOs Pydantic (DocenteCreate, DocenteResponse, TurmaDocenteCreate, etc.)
  - application/services.py → Lógica de negócio: CRUD e vinculação N:M com validação de duplicidade
  - infrastructure/orm_models.py → Modelos ORM: Docente e TurmaDocente (tabela associativa)
"""
