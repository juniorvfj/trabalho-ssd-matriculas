# ADR 003: Segurança com JWT e Role-Based Access Control (RBAC)

## Status
Aceito

## Contexto
Por se tratar do projeto da disciplina "Segurança de Sistemas Distribuídos", os requisitos de segurança e autorização são críticos. Precisávamos implementar um mecanismo stateless que não apenas autenticasse quem realiza a chamada à API, mas também autorizasse com base no papel do usuário dentro da instituição acadêmica, evitando escalonamento de privilégios.

## Decisão
Implementar autenticação baseada em **JSON Web Tokens (JWT)** combinada com um **Role-Based Access Control (RBAC)** em nível de API:
1. **JWT (Bearer Token)**: Utilizado para gerenciar a sessão de forma stateless. Todos os tokens carregam uma assinatura criptografada e uma validade de expiração.
2. **Dependência RoleChecker**: Uma classe de injeção de dependência do FastAPI foi desenvolvida (`RoleChecker`) para injetar explicitamente os perfis (Roles) permitidos em cada rota. As Roles criadas foram: `ADMIN`, `ALUNO`, `COORDENACAO`, `PROCESSAMENTO`, `CONSULTA`.
3. **Senhas**: Todas as senhas são armazenadas no banco de dados com hash forte utilizando o esquema bcrypt via `passlib`.

## Consequências
**Positivas:**
- Abordagem unificada e testável: Testes de API podem validar dinamicamente se o acesso é bloqueado (`HTTP 403 Forbidden`) para perfis errados.
- Integração perfeita com os sistemas de dependência do FastAPI.
- A natureza Stateless elimina a necessidade de manter estado de sessão em memória ou banco em cache (Redis).

**Negativas:**
- Revogar o acesso instantaneamente de um usuário comprometido é mais complexo em sistemas de token JWT, a menos que uma "denylist" (lista de revogação) seja implementada, o que foge ao escopo simplificado da disciplina.
