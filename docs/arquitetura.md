# Arquitetura do Sistema de Matrícula (Monólito Modular)

O sistema foi desenhado sob o paradigma de Orientação a Serviço (SOA) e "Contract-First", consolidado em um **Monólito Modular** usando **FastAPI**.

## Por que Monólito Modular?
1. **Baixo Acoplamento, Alta Coesão**: Reduz o acoplamento de código ao separar regras de negócio de diferentes entidades (ex: Cursos vs Alunos), sem a complexidade operacional da gestão de microserviços (network falhas, orquestração Kubernetes, etc).
2. **Camadas Claras**: Cada módulo tem sua própria divisão em `api/`, `application/`, `infrastructure/` (e `domain/` nos módulos com regras puras de negócio, como disciplinas e históricos).
3. **Escopo Acadêmico**: É mais que suficiente para simular SOA, pois garantimos que as interações entre os módulos ocorram por meio de interfaces (serviços de aplicação/tarefas) e não acessando banco de dados diretamente de outro domínio.

## Camadas Internas de Cada Módulo

- **`api/`**: Camada de roteamento (FastAPI) e Models Pydantic de Request/Response. Só se comunica com a camada de `application`.
- **`application/`**: Regras de orquestração ("Use Cases"). Recebe dados da `api`, busca regras no `domain` e salva na `infrastructure`.
- **`domain/`**: Entidades core do negócio e regras que independem de framework. Nenhum acesso a banco acontece aqui. Regras de elegibilidade pura.
- **`infrastructure/`**: ORM SQLAlchemy (Models e Repositories). Onde o acesso ao PostgreSQL acontece efetivamente. Os modelos espelham fielmente o **schema físico SIGAA** do professor.

## Modelo Conceitual Compartilhado (`app/shared/schemas/`)

Camada transversal que materializa o **modelo conceitual do diagrama de entidades**
(`docs/diagrams/`) sobre o schema físico, no padrão dos contratos de referência do professor:

- **`Resource`**: base de todo recurso da API (`resourceType` como discriminador + `id`).
- **Objetos de valor derivados** das colunas planas: `PeriodoLetivo {ano, periodo}`
  (← `varchar(5)` `'20182'`), `CargaHoraria` (da Disciplina: teórica/prática/extensionista;
  do Currículo: totalMinima/obrigatoriaTotal/...), `Prazo {minimo, medio, maximo}`.
- **Herança**: `Disciplina` → `DisciplinaCurriculo` (+ `tipo`, `nivel`) e
  `DisciplinaHistoricoAcademico` (+ `mencao`, `frequencia`, `status`, `periodoLetivo`).
  A herança de classes Pydantic é exportada como **`allOf`** nos contratos OpenAPI — o mesmo
  padrão OO dos YML de referência (`professor_material/*.yml`).
- **Variantes `_Short`** (`AlunoShort`, `CursoShort`, `CurriculoShort`) para referências
  resumidas entre recursos.

O princípio (extraído do `SIGAA-API.sql` do professor): **o banco permanece fiel ao DDL físico;
a API expõe o modelo conceitual, derivando os campos em tempo de consulta**. O de-para completo
campo a campo está em [`mapeamento-conceitual-fisico.md`](mapeamento-conceitual-fisico.md).

## Padrões de SOA e Contract-First
- Todos os endpoints respeitam os contratos OpenAPI, definidos por serviço em `docs/openapi/*.yml`
  (padrão `allOf` + `Resource` com discriminator) e materializados via **Pydantic** e **FastAPI**.
- Listagens usam o envelope **`SearchSet`** (`total`, `count`, `offset`, links HATEOAS, `items`).
- O modelo canônico de erro é global na API (implementado via global exception handler em `app/core/exceptions.py`).
