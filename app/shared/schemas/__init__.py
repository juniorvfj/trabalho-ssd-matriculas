"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Schemas conceituais compartilhados — modelo de entidades (diagrama) sobre o schema físico SIGAA.

Materializa na API o modelo conceitual de `docs/diagrams/Modelo de Entidades`, no padrão dos
contratos de referência do professor (`professor_material/*.yml`):

- classe base `Resource` com o discriminador `resourceType`;
- objetos de valor derivados de colunas planas (`PeriodoLetivo`, `CargaHoraria`, `Prazo`);
- herança: `Disciplina` → `DisciplinaCurriculo` / `DisciplinaHistoricoAcademico`, que o
  Pydantic/FastAPI exporta como `allOf` no OpenAPI — o mesmo padrão dos YML do professor;
- variantes `_Short` para referências entre recursos (`AlunoShort`, `CursoShort`...).

Os campos usam os nomes camelCase do diagrama porque estes modelos SÃO o contrato JSON.
O de-para completo diagrama ↔ colunas ↔ JSON está em docs/mapeamento-conceitual-fisico.md.
"""
from typing import Optional

from pydantic import BaseModel, Field

# Menções de aprovação no SIGAA (SS=Superior, MS=Médio Superior, MM=Médio).
# Fonte única — usada aqui (status da disciplina cursada) e por verificarElegibilidade.
MENCOES_APROVACAO = {"SS", "MS", "MM"}

# Domínios de status conceituais (diagrama/YML do professor) ← códigos de 1 letra do banco
STATUS_CURRICULO = {"A": "ativo", "I": "inativo"}
STATUS_VINCULO_ALUNO = {"A": "ativo", "I": "inativo", "C": "concluido"}


def _int(v) -> Optional[int]:
    """Numeric do banco → int do JSON (None preservado)."""
    return int(v) if v is not None else None


def is_ead(modalidade: Optional[str]) -> bool:
    """Modalidade a distância? (no DDL a modalidade é texto livre: 'Presencial', 'A Distância'...)."""
    if not modalidade:
        return False
    m = modalidade.lower()
    return "dist" in m or "ead" in m


def status_disciplina_cursada(mencao: Optional[str]) -> str:
    """
    Status conceitual da disciplina no histórico, derivado da menção
    (enum do HistoricoAcademico.yml do professor). Sem menção lançada = 'cursando'.
    """
    if not mencao:
        return "cursando"
    return "aprovado" if mencao in MENCOES_APROVACAO else "reprovado"


# ── Base e objetos de valor ──────────────────────────────────────────────────────


class Resource(BaseModel):
    """Base de todo recurso da API (padrão `Resource` dos YML do professor)."""
    resourceType: str
    id: Optional[str] = None


class PeriodoLetivo(BaseModel):
    """Período letivo conceitual {ano, periodo} ← varchar(5) 'AAAAP' do banco."""
    ano: Optional[int] = None
    periodo: Optional[int] = None

    @classmethod
    def from_sigaa(cls, valor: Optional[str]) -> Optional["PeriodoLetivo"]:
        """'20182' → PeriodoLetivo(ano=2018, periodo=2); None/malformado → None."""
        if not valor or len(valor) < 5 or not valor[:5].isdigit():
            return None
        return cls(ano=int(valor[:4]), periodo=int(valor[4:5]))


class CargaHorariaDisciplina(BaseModel):
    """CargaHoraria da Disciplina (diagrama). 'extensionista' não tem coluna no DDL → null."""
    teorica: Optional[int] = None
    pratica: Optional[int] = None
    extensionista: Optional[int] = None


class CargaHorariaCurriculo(BaseModel):
    """
    CargaHoraria do Currículo (diagrama). 'obrigatoriaAula', 'obrigatoriaOrientacao' e
    'minimaPeriodo' não têm coluna no DDL → null (mapeamento, Seção 2.3).
    """
    totalMinima: Optional[int] = None
    obrigatoriaAula: Optional[int] = None
    obrigatoriaOrientacao: Optional[int] = None
    obrigatoriaTotal: Optional[int] = None
    optativaMinima: Optional[int] = None
    maximaEletivos: Optional[int] = None
    maximaPeriodo: Optional[int] = None
    minimaPeriodo: Optional[int] = None


class Prazo(BaseModel):
    """Prazo do Currículo em períodos ← MIN_PERIODOS / NUM_PERIODOS / MAX_PERIODOS."""
    minimo: Optional[int] = None
    medio: Optional[int] = None
    maximo: Optional[int] = None


# ── Variantes _Short (referências entre recursos) ────────────────────────────────


class UnidadeOrganizacionalShort(Resource):
    resourceType: str = "UnidadeOrganizacional"
    nome: Optional[str] = None


class CursoShort(Resource):
    resourceType: str = "Curso"
    codigo: Optional[str] = None
    nome: Optional[str] = None


class CurriculoShort(Resource):
    resourceType: str = "Curriculo"
    codigo: Optional[str] = None


class AlunoShort(Resource):
    resourceType: str = "Aluno"
    matricula: Optional[str] = None
    nome: Optional[str] = None
    curso: Optional[CursoShort] = None


# ── Disciplina e suas especializações (herança → allOf no OpenAPI) ───────────────


class Disciplina(Resource):
    """Entidade Disciplina do diagrama (campos-base herdados pelas especializações)."""
    resourceType: str = "Disciplina"
    codigo: Optional[str] = None
    nome: Optional[str] = None
    modalidade: Optional[str] = None
    cargaHorariaTotal: Optional[int] = Field(
        None, description="Derivado: teórica + prática (SIGAA-API.sql, l. 10)"
    )
    cargaHorariaPresencial: Optional[CargaHorariaDisciplina] = None
    cargaHorariaEad: Optional[CargaHorariaDisciplina] = None
    unidadeOrganizacional: Optional[UnidadeOrganizacionalShort] = None


class DisciplinaCurriculo(Disciplina):
    """Disciplina no contexto do Currículo (componente curricular): herda tudo + tipo/nivel."""
    tipo: Optional[str] = Field(None, description="'Obrigatória'/'Optativa' ← TIPO ('OBR'/'OPT')")
    nivel: Optional[int] = Field(None, description="Nível/semestre sugerido ← coluna PERIODO")


class DisciplinaHistoricoAcademico(Disciplina):
    """Disciplina cursada (contexto do Histórico): herda tudo + menção/frequência/status/período."""
    mencao: Optional[str] = None
    frequencia: Optional[int] = Field(None, description="Sem coluna no DDL do professor → null")
    status: Optional[str] = Field(None, description="Derivado da menção: aprovado/reprovado/cursando")
    periodoLetivo: Optional[PeriodoLetivo] = None


def disciplina_para_conceitual(d, unidade_nome: Optional[str] = None) -> dict:
    """
    Campos-base da Disciplina conceitual a partir da linha ORM de SIGAA_DISCIPLINA.

    Regras de derivação (mapeamento, Seções 2.2 e 4.1):
    - cargaHorariaTotal = teórica + prática; a coluna extra CARGA_HORARIA (exemplo didático
      do projeto, fora do DDL do professor) prevalece quando preenchida;
    - a modalidade decide qual associação de CargaHoraria é preenchida
      (presencial × EAD) — a outra fica nula, como no diagrama (0..1 cada).

    Retorna kwargs para construir Disciplina ou qualquer especialização dela.
    """
    teorica = _int(d.carga_horaria_teorica)
    pratica = _int(d.carga_horaria_pratica)
    total = _int(getattr(d, "carga_horaria", None))
    if total is None:
        total = (teorica or 0) + (pratica or 0)
    carga = CargaHorariaDisciplina(teorica=teorica, pratica=pratica)
    return {
        "id": d.id,
        "codigo": d.id,
        "nome": d.nome,
        "modalidade": d.modalidade,
        "cargaHorariaTotal": total,
        "cargaHorariaPresencial": None if is_ead(d.modalidade) else carga,
        "cargaHorariaEad": carga if is_ead(d.modalidade) else None,
        "unidadeOrganizacional": UnidadeOrganizacionalShort(id=d.unidade, nome=unidade_nome),
    }
