"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Rotas (API Layer) de Currículo (Estrutura Curricular) — modelo SIGAA.

Os retornos seguem o modelo conceitual do diagrama: 'cargaHoraria' e 'prazo' como
objetos de valor, 'periodoLetivoVigor' como PeriodoLetivo e os componentes
curriculares como Disciplina_Curriculo (herança de Disciplina, como nos YML de
referência do professor). De-para: docs/mapeamento-conceitual-fisico.md.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.shared.responses import SearchSet, search_set
from app.shared.schemas import (
    STATUS_CURRICULO,
    CargaHorariaCurriculo,
    CursoShort,
    DisciplinaCurriculo,
    PeriodoLetivo,
    Prazo,
    disciplina_para_conceitual,
    _int,
)
from app.modules.curriculos.api.schemas import (
    CurriculoCreate,
    CurriculoDisciplinaCreate,
    CurriculoResponse,
)
from app.modules.curriculos.application.services import (
    add_disciplina,
    create_curriculo,
    get_curriculo,
    get_curso_do_curriculo,
    get_disciplinas_do_curriculo,
    search_curriculos,
)

router = APIRouter()


def _db_id(url_id: str) -> str:
    """
    Converte o id do currículo da forma usada na URL para a forma armazenada no SIGAA
    ('6351/2'). Aceita a convenção do professor ('6351.2', ver SIGAA-API.sql e a
    collection Postman), a variante com hífen do Aluno.yml ('6351-3'), a forma compacta
    ('63512') e a já armazenada ('6351/2').
    """
    for sep in (".", "-"):
        if sep in url_id:
            return url_id.replace(sep, "/")
    if "/" in url_id:
        return url_id
    return f"{url_id[:4]}/{url_id[4:]}"


def _url_id(db_id: str) -> str:
    """Forma pública do id do currículo ('6351/2' → '6351.2'), como nos exemplos do professor."""
    return db_id.replace("/", ".")


# Rótulos do tipo de componente curricular. O SIGAA armazena o código ('OBR'/'OPT') e o
# SIGAA-API.sql do professor expõe o rótulo legível — mesma convenção adotada aqui.
TIPO_LABELS = {"OBR": "Obrigatória", "OPT": "Optativa"}
TIPO_CODIGOS = {label: codigo for codigo, label in TIPO_LABELS.items()}


def _tipo_label(codigo: Optional[str]) -> Optional[str]:
    """Código armazenado → rótulo legível (ex.: 'OBR' → 'Obrigatória')."""
    return TIPO_LABELS.get(codigo, codigo)


def _tipo_codigo(valor: Optional[str]) -> Optional[str]:
    """
    Normaliza o filtro de tipo para o código armazenado.

    Aceita tanto o rótulo do professor ('Obrigatória') quanto o código cru ('OBR'),
    para não quebrar quem já consome a API pelo código.
    """
    return TIPO_CODIGOS.get(valor, valor) if valor else None


def _curriculo_response(c, curso=None) -> CurriculoResponse:
    """Linha de SIGAA_CURRICULO → Currículo conceitual (mapeamento, Seção 4.2)."""
    return CurriculoResponse(
        id=_url_id(c.id),
        codigo=_url_id(c.id),
        status=STATUS_CURRICULO.get(c.status, c.status),
        periodoLetivoVigor=PeriodoLetivo.from_sigaa(c.periodo_letivo_vigor),
        cargaHoraria=CargaHorariaCurriculo(
            totalMinima=_int(c.carga_horaria_minima_total),
            obrigatoriaTotal=_int(c.carga_horaria_obr),
            optativaMinima=_int(c.carga_horaria_minima_opt),
            maximaEletivos=_int(c.carga_horaria_eletiva_max),
            maximaPeriodo=_int(c.carga_horaria_max_periodo),
        ),
        prazo=Prazo(
            minimo=_int(c.min_periodos),
            medio=_int(c.num_periodos),
            maximo=_int(c.max_periodos),
        ),
        curso=CursoShort(id=curso.id, codigo=curso.id, nome=curso.nome) if curso else None,
    )


def _componente(cd, disc) -> DisciplinaCurriculo:
    """Componente curricular = Disciplina_Curriculo: herda a Disciplina + tipo/nivel."""
    return DisciplinaCurriculo(
        **disciplina_para_conceitual(disc),
        tipo=_tipo_label(cd.tipo),
        nivel=_int(cd.periodo),
    )


@router.post("/", response_model=CurriculoResponse, status_code=status.HTTP_201_CREATED)
async def create(curriculo_in: CurriculoCreate, db: AsyncSession = Depends(get_db)):
    """Cria um novo currículo (SIGAA_CURRICULO) e o vínculo com o curso, se informado."""
    c = await create_curriculo(db, curriculo_in)
    curso = await get_curso_do_curriculo(db, c.id)
    return _curriculo_response(c, curso)


@router.get("/", response_model=SearchSet)
async def list_curriculos(
    db: AsyncSession = Depends(get_db),
    curso: Optional[str] = Query(None, description="Filtro por código de curso"),
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset"),
):
    """Pesquisa currículos, opcionalmente por curso (SearchSet)."""
    curriculos, total = await search_curriculos(db, curso, _offset, _count)
    # Itens resumidos, como na consulta de listagem do SIGAA-API.sql (id, status, vigência)
    items = [
        {
            "resourceType": "Curriculo",
            "id": _url_id(c.id),
            "codigo": _url_id(c.id),
            "status": STATUS_CURRICULO.get(c.status, c.status),
            "periodoLetivoVigor": (
                p.model_dump() if (p := PeriodoLetivo.from_sigaa(c.periodo_letivo_vigor)) else None
            ),
        }
        for c in curriculos
    ]
    extra = f"curso={curso}&" if curso else ""
    return search_set(items, total, _offset, _count, "/api/Curriculo", extra)


@router.get("/{id}", response_model=CurriculoResponse)
async def read(id: str, db: AsyncSession = Depends(get_db)):
    """Detalha um currículo: cargaHoraria e prazo como objetos, vigência e curso."""
    c = await get_curriculo(db, _db_id(id))
    curso = await get_curso_do_curriculo(db, c.id)
    return _curriculo_response(c, curso)


@router.get("/{id}/disciplina", response_model=SearchSet)
@router.get("/{id}/disciplinas", response_model=SearchSet, include_in_schema=False)
async def list_disciplinas(
    id: str,
    db: AsyncSession = Depends(get_db),
    nivel: Optional[int] = Query(None, description="Filtro por nível/semestre sugerido (coluna PERIODO)"),
    tipo: Optional[str] = Query(None, description="Filtro por tipo ('Obrigatória'/'Optativa' ou 'OBR'/'OPT')"),
):
    """
    Lista os componentes curriculares como Disciplina_Curriculo (herança de Disciplina).

    Cada item carrega os campos herdados da Disciplina (nome, modalidade, cargas
    horárias) mais os da especialização ('tipo' legível e 'nivel', como no
    SIGAA-API.sql do professor). O caminho segue o padrão do professor
    (/Curriculo/{id}/disciplina); o plural é mantido por compatibilidade.
    """
    db_id = _db_id(id)
    await get_curriculo(db, db_id)
    linhas = await get_disciplinas_do_curriculo(db, db_id, nivel, _tipo_codigo(tipo))
    items = [_componente(cd, disc).model_dump() for cd, disc in linhas]
    extra = ""
    if nivel is not None:
        extra += f"nivel={nivel}&"
    if tipo:
        extra += f"tipo={tipo}&"
    return search_set(
        items, len(items), 0, len(items) or 1, f"/api/Curriculo/{id}/disciplina", extra
    )


@router.get("/{id}/disciplina/{disciplina}", response_model=DisciplinaCurriculo)
async def read_disciplina(id: str, disciplina: str, db: AsyncSession = Depends(get_db)):
    """Detalha um componente curricular específico (padrão do professor: /disciplina/{id})."""
    db_id = _db_id(id)
    await get_curriculo(db, db_id)
    linhas = await get_disciplinas_do_curriculo(db, db_id)
    for cd, disc in linhas:
        if disc.id == disciplina:
            return _componente(cd, disc)
    raise HTTPException(status_code=404, detail="Disciplina não pertence a este currículo")


@router.post("/{id}/disciplina", status_code=status.HTTP_201_CREATED)
@router.post("/{id}/disciplinas", status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def add_disciplina_to_curriculo(id: str, disc_in: CurriculoDisciplinaCreate, db: AsyncSession = Depends(get_db)):
    """Vincula uma disciplina como componente do currículo (SIGAA_RL_CURRICULO_DISCIPLINA)."""
    await add_disciplina(db, _db_id(id), disc_in)
    return {
        "resourceType": "Disciplina",
        "curriculo": _url_id(_db_id(id)),
        "id": disc_in.disciplina,
        "codigo": disc_in.disciplina,
        "nivel": disc_in.periodo,
        "tipo": _tipo_label(disc_in.tipo),
    }
