"""
Pacote core — Infraestrutura transversal da aplicação.

Contém os módulos de suporte que são usados por todos os outros pacotes:

- config.py     → Variáveis de ambiente e configurações (Pydantic Settings)
- database.py   → Engine assíncrona, SessionLocal e Base declarativa (SQLAlchemy 2.0)
- security.py   → Geração de JWT, hash bcrypt e verificação de senhas
- exceptions.py → Modelo Canônico de Erro e handlers globais de exceção
- logging.py    → Configuração centralizada do logger da aplicação
"""
