"""
Pacote modules — Módulos de Domínio do sistema acadêmico.

Cada sub-pacote representa uma entidade ou agregado de negócio e segue
a mesma estrutura de camadas (Layered Architecture):

    módulo/
    ├── api/               → Schemas (DTOs Pydantic) e Router (endpoints FastAPI)
    ├── application/       → Serviços de negócio (orquestração e regras)
    └── infrastructure/    → Modelos ORM (SQLAlchemy) e repositórios

Módulos disponíveis:
- alunos                → Serviço de Entidade — Aluno
- cursos                → Serviço de Entidade — Curso
- disciplinas           → Serviço de Entidade — Disciplina (com pré-requisitos)
- turmas                → Serviço de Entidade — Turma + Período Letivo
- historicos            → Serviço de Entidade — Histórico Acadêmico
- matriculas            → Serviço de Entidade — Matrícula + Solicitação + Elegibilidade
- curriculos            → Serviço de Entidade — Currículo (grade curricular)
- docentes              → Serviço de Entidade — Docente (professor/coordenador)
- unidades_organizacionais → Serviço de Entidade — Departamento/Instituto
- usuarios              → Serviço de Entidade — Usuário (autenticação e RBAC)
"""
