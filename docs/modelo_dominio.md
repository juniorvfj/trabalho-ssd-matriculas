# Modelo de Domínio - Matrícula

## Entidades e Relacionamentos

De acordo com o documento base:

1. **Curso**
   - Atributos base: `id` (integer), `codigo` (string, max 10), `nome` (string, max 100), `ativo` (boolean)
   - Relacionamentos: Vários alunos, Várias disciplinas

2. **Aluno**
   - Atributos base: `id` (integer), `matricula` (string, 9 dígitos), `nome` (string, max 150), `email` (string formato email), `data_admissao` (string data iso8601), `ira` (float entre 0.0 e 5.0), `limite_creditos_periodo` (integer entre 1 e 40), `curso_id` (integer FK), `ativo` (boolean default true)

3. **Disciplina**
   - Atributos base: `id`, `codigo`, `nome`, `creditos`, `carga_horaria`, `curso_id`, `ativa`
   - Pré-requisitos: Auto-relacionamento ou tabela associativa (`DisciplinaPrerequisito`).

4. **Turma**
   - Atributos base: `id`, `disciplina_id`, `periodo_letivo_id`, `codigo_turma`, `vagas_totais`, `vagas_ocupadas`, `horario_serializado`, `ativa`

5. **Matrícula / Solicitação de Matrícula**
   - Onde residem os estados do processamento ("fases").
   - Solicitação: `aluno_id`, `turma_id`, `prioridade`, `fase`, `status`
   - Matrícula Efetivada: Gerada após as fases do processamento confirmarem a elegibilidade e vaga.

## Regras Core de Negócio (Elegibilidade)
- O Aluno não pode estar matriculado acima do limite de créditos.
- A Disciplina deve ser do currículo do Curso do aluno.
- O aluno precisa ter os pré-requisitos (avaliado pelo Histórico).
- Conflito de Horário: cruzamento do campo `horario_serializado` das Turmas selecionadas.
