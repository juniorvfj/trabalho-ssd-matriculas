import os
import re
import glob

mapping = {
    'aluno_api.v1.yml': ('Aluno', 'alunos'),
    'auth_api.v1.yml': ('Auth', 'auth'),
    'curriculo_api.v1.yml': ('Curriculo', 'curriculos'),
    'curso_api.v1.yml': ('Curso', 'cursos'),
    'disciplina_api.v1.yml': ('Disciplina', 'disciplinas'),
    'docente_api.v1.yml': ('Docente', 'docentes'),
    'elegibilidade_api.v1.yml': ('Elegibilidade', 'elegibilidade'),
    'historico_api.v1.yml': ('HistoricoAcademico', 'historicos'),
    'matricula_api.v1.yml': ('Matricula', 'matriculas'),
    'turma_api.v1.yml': ('Turma', 'turmas'),
    'unidade_organizacional_api.v1.yml': ('UnidadeOrganizacional', 'unidades_organizacionais')
}

resource_schema = """
    Resource:
      type: object
      required:
        - resourceType
      properties:
        id:
          type: string
          description: id único da instânica
        resourceType:
          type: string
        lastUpdated:
          type: string
          format: date-time
      discriminator:
        propertyName: resourceType
        mapping:
          Aluno: '#/components/schemas/Aluno'
          Curso: '#/components/schemas/Curso'
          Curriculo: '#/components/schemas/Curriculo'
          Disciplina: '#/components/schemas/Disciplina'
          Docente: '#/components/schemas/Docente'
          HistoricoAcademico: '#/components/schemas/HistoricoAcademico'
          Matricula: '#/components/schemas/Matricula'
          Turma: '#/components/schemas/Turma'
          UnidadeOrganizacional: '#/components/schemas/UnidadeOrganizacional'
"""

search_set_schema = """
    SearchSet:
      type: object  
      required:
        - total
        - link
      properties:
        total:
          type: integer 
        count:
          type: integer
        offset:
          type: integer     
        link:
          type: object
          required:
            - self
          properties:
            self:
              type: string
            next:
              type: string
            previous:
              type: string
        items:
          type: array
          items:
            anyOf:
            - $ref: '#/components/schemas/AlunoResponse'
            - $ref: '#/components/schemas/CursoResponse'
            - $ref: '#/components/schemas/CurriculoResponse'
            - $ref: '#/components/schemas/DisciplinaResponse'
            - $ref: '#/components/schemas/DocenteResponse'
            - $ref: '#/components/schemas/HistoricoAcademicoResponse'
            - $ref: '#/components/schemas/MatriculaResponse'
            - $ref: '#/components/schemas/TurmaResponse'
            - $ref: '#/components/schemas/UnidadeOrganizacionalResponse'
"""

base_dir = r"c:\Users\junio\OneDrive\AAMestrado\2026.1\Segurança de Sistemas Distribuidos\TrabalhoSSD\docs\openapi"

for filepath in glob.glob(os.path.join(base_dir, "*.yml")):
    filename = os.path.basename(filepath)
    if filename not in mapping:
        continue
    entity_name, url_path = mapping[filename]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace servers block
    content = re.sub(
        r'servers:.*?(?=security:|paths:|components:)', 
        f'servers:\n  - url: /api/{entity_name}\n\n', 
        content, 
        flags=re.DOTALL
    )

    # Replace paths
    content = re.sub(rf'/api/v1/{url_path}/:', '/:', content)
    content = re.sub(rf'/api/v1/{url_path}/{{id}}:', '/{id}:', content)
    content = re.sub(rf'/api/v1/{url_path}/', '/', content)
    content = re.sub(rf'/api/v1/{url_path}:', '/:', content)
    # in historical endpoints, there's /api/v1/historicos/aluno/{aluno_id}:
    content = re.sub(rf'/api/v1/{url_path}/aluno/', '/aluno/', content)

    # Delete existing [EntityName]SearchSet block entirely, or generic SearchSet
    # Using a regex that captures everything until the next outdented schema name
    content = re.sub(r'^[ \t]{4}SearchSet:.*?(?=\n[ \t]{4}[A-Za-z0-9_]+:|\Z)', '', content, flags=re.DOTALL | re.MULTILINE)
    content = re.sub(r'^[ \t]{4}' + entity_name + r'SearchSet:.*?(?=\n[ \t]{4}[A-Za-z0-9_]+:|\Z)', '', content, flags=re.DOTALL | re.MULTILINE)

    # Convert EntitySearchSet to SearchSet in the paths
    content = re.sub(rf'#/components/schemas/{entity_name}SearchSet', '#/components/schemas/SearchSet', content)

    # If schemas: is found, inject Resource
    if 'Resource:' not in content:
        content = re.sub(r'(schemas:\s*\n)', r'\1' + resource_schema, content)
    
    # Inject SearchSet at the very end of the file
    content += search_set_schema

    # Make the {EntityName}Response implement Resource
    entity_response = f"{entity_name}Response"
    replace_str = f"{entity_response}:\n      allOf:\n        - $ref: '#/components/schemas/Resource'\n        - type: object"
    content = re.sub(rf'{entity_response}:\s+type: object', replace_str, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Modification complete.")
