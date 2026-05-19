# Relatório de Refatoração OpenAPI

Este relatório descreve as alterações realizadas nos contratos OpenAPI e na camada de APIs (backend) do projeto `TrabalhoSSD`, adequando-o às novas especificações formais do professor com base no documento de Análise Orientada a Serviços.

## 1. Escopo das Alterações

### 1.1 Contratos OpenAPI (`docs/openapi`)
Os seguintes arquivos foram substituídos e adaptados de acordo com as especificações do professor, localizadas na pasta `professor_material/`:
*   **`aluno_api.v1.yml`**: Refatorado para incorporar os novos parâmetros de pesquisa (`nome`, `curso`, `curriculo`, `periodoIngresso`, `_count`, `_offset`) e o padrão `SearchSet`.
*   **`historico_api.v1.yml`**: Refatorado para alinhar as rotas com a nova estrutura, incluindo o sub-recurso `/{id}/disciplina` (que aceita os parâmetros `periodoLetivo`, `status`, e `disciplina`).
*   **`matricula_api.v1.yml`**: Refatorado para refletir o modelo de operações em lote. A rota POST agora espera um array, e foi implementada a rota PATCH para uso exclusivo da restrição de campos (`status` e `motivoIndeferimento`).

### 1.2 Camada de Aplicação (`app/main.py`)
Os prefixos das rotas de serviço de entidade foram atualizados para padronização exata da nomenclatura, como definido nos arquivos de especificação. As alterações incluem:
*   `alunos_router` agora responde no caminho raiz: `/api/Aluno`
*   `historicos_router` agora responde no caminho raiz: `/api/HistoricoAcademico`
*   `matriculas_router` agora responde no caminho raiz: `/api/Matricula`

### 1.3 Controladores / Routers
Para refletir os novos contratos e comportamentos, os seguintes routers foram refatorados:

*   **`app/modules/alunos/api/router.py`**:
    *   Substituição de `get_all_alunos` pelo método `search` (`GET /`).
    *   Implementação do padrão de saída `SearchSet`, agrupando os itens com paginação customizada.

*   **`app/modules/historicos/api/router.py`**:
    *   Consolidação das rotas para `GET /{id}`.
    *   Criação da rota `GET /{id}/disciplina` permitindo filtrar as disciplinas no histórico através de query params.

*   **`app/modules/matriculas/api/router.py`**:
    *   O endpoint `GET /` foi recriado para exigir os parâmetros descritos (`periodoLetivo` obrigatório; pelo menos um entre `aluno` ou `turma`).
    *   O endpoint `POST /` foi adaptado para receber e retornar arrays.
    *   Implementação do `PATCH /{id}` que aplica alterações apenas para os campos `/status` e `/motivoIndeferimento` usando formato JSON Patch.

---

## 2. Exemplos de Payload

### 2.1 Aluno (Search)
**Request:** `GET /api/Aluno?nome=João&_count=10&_offset=0`

**Response:**
```json
{
  "total": 1,
  "count": 1,
  "offset": 0,
  "link": {
    "self": "/api/Aluno?_offset=0&_count=10",
    "next": "",
    "previous": ""
  },
  "items": [
    {
      "resourceType": "Aluno",
      "id": "1",
      "matricula": "123456789",
      "nome": "João",
      "curso": {
        "resourceType": "Curso",
        "id": "1"
      }
    }
  ]
}
```

### 2.2 Matricula (Create Batch)
**Request:** `POST /api/Matricula`
```json
[
  {
    "aluno": { "id": "1" },
    "turma": { "id": "1" },
    "status": "pedido"
  }
]
```

**Response (201 Created):**
```json
[
  {
    "resourceType": "Matricula",
    "id": "100",
    "status": "pedido",
    "aluno": { "id": "1" },
    "turma": { "id": "1" }
  }
]
```

### 2.3 Matricula (Patch)
**Request:** `PATCH /api/Matricula/100`
```json
[
  {
    "op": "replace",
    "path": "/status",
    "value": "indeferido"
  },
  {
    "op": "replace",
    "path": "/motivoIndeferimento",
    "value": "Falta de pré-requisito"
  }
]
```

**Response (200 OK):**
```json
[
  {
    "resourceType": "Matricula",
    "id": "100",
    "status": "indeferido",
    "aluno": { "id": "1" },
    "turma": { "id": "1" }
  }
]
```

---

## 3. Impactos na Arquitetura

1.  **Desacoplamento e Granularidade**: A mudança principal foi adaptar o sistema para uma **Análise Orientada a Serviços**, onde os endpoints refletem de maneira mais estrita as entidades de domínio e os comandos de negócio, ao invés de simples mapeamento CRUD de banco de dados. 
2.  **Padronização de Paginação e Filtragem (`SearchSet`)**: Ao centralizar o padrão `SearchSet`, as APIs adquirem uma arquitetura mais consistente, preparando a plataforma para consultas paginadas unificadas, útil para a possível integração com Gateways API e BFFs (Backend-for-Frontend).
3.  **Processamento em Lote (Batch)**: O serviço `Matricula` ao processar arrays em requisições de criação exige que a validação de regra de negócio seja robusta o suficiente para lidar com processamentos concorrentes ou em série para múltiplos alunos simultaneamente.
4.  **Operação Semântica Restrita (PATCH)**: Ao restringir as atualizações na Matrícula para o esquema de JSON Patch para campos pontuais (`status` e `motivoIndeferimento`), mitigou-se a possibilidade de atualizações indevidas no banco de dados (ex: mudar o `aluno_id` ou `turma_id` em uma matrícula preexistente).
