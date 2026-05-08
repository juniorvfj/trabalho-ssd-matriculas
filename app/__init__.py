"""
Pacote raiz da aplicação (app).

Este pacote contém toda a lógica do Sistema de Matrícula de Alunos de Graduação,
organizado como um Monólito Modular com os seguintes sub-pacotes:

- core/       → Configuração, banco de dados, segurança, exceções e logging
- api/        → Roteadores globais (autenticação) e dependências (JWT, RBAC)
- modules/    → Módulos de domínio (Alunos, Cursos, Disciplinas, Turmas, etc.)
- shared/     → Utilitários e modelos compartilhados entre módulos

Disciplina: Segurança em Sistemas Distribuídos — UnB
Autores: Vicente Jr., Brenno Ribeiro e Rosane Pinheiro
Professor: Ricardo Staciarini Puttini
"""
