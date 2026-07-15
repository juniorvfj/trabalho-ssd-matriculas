"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Rotas (API Layer) de Currículo (Estrutura Curricular) — modelo SIGAA.

Endpoints seguindo as consultas de "Estrutura Curricular" do SIGAA-API.sql:
pesquisa (opcionalmente por curso), detalhe com cargas/períodos e listagem de
disciplinas do currículo.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.shared.responses import SearchSet, search_set
from app.modules.curriculos.api.schemas import (
    CurriculoCreate,
    CurriculoDisciplinaCreate,
    CurriculoResponse,
)
from app.modules.curriculos.application.services import (
    add_disciplina,
    create_curriculo,
    get_curriculo,
    get_disciplinas_do_curriculo,
    search_curriculos,
)

router = APIRouter()


def _int(v) -> Optional[int]:
    return int(v) if v is not None else None


def _periodo(pv: str) -> dict:
    return {"ano": pv[:4] or None, "numero": pv[4:] or None}


def _db_id(url_id: str) -> str:
    """
    Converte o id do currículo da forma usada na URL (sem barra, ex.: '63512')
    para a forma armazenada no SIGAA (com barra: '6351/2'). Mesma convenção do
    SIGAA-API.sql do professor, evitando o problema de '/' em path param.
    Aceita também a forma já com barra (idempotente).
    """
    return url_id if "/" in url_id else f"{url_id[:4]}/{url_id[4:]}"


def _url_id(db_id: str) -> str:
    """Forma sem barra do id do currículo, segura para uso em path (ex.: '6351/2' → '63512')."""
    return db_id.replace("/", "")


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


@router.post("/", response_model=CurriculoResponse, status_code=status.HTTP_201_CREATED)
async def create(curriculo_in: CurriculoCreate, db: AsyncSession = Depends(get_db)):
    """Cria um novo currículo (SIGAA_CURRICULO) e o vínculo com o curso, se informado."""
    return await create_curriculo(db, curriculo_in)


@router.get("/", response_model=SearchSet)
async def list_curriculos(
    db: AsyncSession = Depends(get_db),
    curso: Optional[str] = Query(None, description="Filtro por código de curso"),
    _count: int = Query(10, alias="_count", ge=1, le=100),
    _offset: int = Query(0, alias="_offset"),
):
    """Pesquisa currículos, opcionalmente por curso (SearchSet)."""
    curriculos, total = await search_curriculos(db, curso, _offset, _count)
    items = [
        {
            "resourceType": "Curriculo",
            "id": _url_id(c.id),
            "status": c.status,
            "periodoLetivoVigor": _periodo(c.periodo_letivo_vigor),
        }
        for c in curriculos
    ]
    extra = f"curso={curso}&" if curso else ""
    return search_set(items, total, _offset, _count, "/api/Curriculo", extra)


@router.get("/{id}")
async def read(id: str, db: AsyncSession = Depends(get_db)):
    """Detalha um currículo: cargas horárias, quantidade de períodos e vigência."""
    c = await get_curriculo(db, _db_id(id))
    return {
        "resourceType": "Curriculo",
        "id": _url_id(c.id),
        "status": c.status,
        "periodoLetivoVigor": _periodo(c.periodo_letivo_vigor),
        "cargaHorariaMinimaTotal": _int(c.carga_horaria_minima_total),
        "cargaHorariaMinimaOpt": _int(c.carga_horaria_minima_opt),
        "cargaHorariaObr": _int(c.carga_horaria_obr),
        "cargaHorariaEletivaMax": _int(c.carga_horaria_eletiva_max),
        "cargaHorariaMaxPeriodo": _int(c.carga_horaria_max_periodo),
        "numPeriodos": _int(c.num_periodos),
        "minPeriodos": _int(c.min_periodos),
        "maxPeriodos": _int(c.max_periodos),
    }


@router.get("/{id}/disciplinas", response_model=SearchSet)
async def list_disciplinas(
    id: str,
    db: AsyncSession = Depends(get_db),
    nivel: Optional[int] = Query(None, description="Filtro por nível/semestre sugerido (coluna PERIODO)"),
    tipo: Optional[str] = Query(None, description="Filtro por tipo ('Obrigatória'/'Optativa' ou 'OBR'/'OPT')"),
):
    """
    Lista as disciplinas (componentes curriculares) de um currículo.

    Segue o SIGAA-API.sql do professor: o componente é filtrado por 'nivel' (coluna PERIODO)
    e por 'tipo', e o tipo é devolvido com o rótulo legível.
    """
    db_id = _db_id(id)
    await get_curriculo(db, db_id)
    linhas = await get_disciplinas_do_curriculo(db, db_id, nivel, _tipo_codigo(tipo))
    items = [
        {
            "resourceType": "CurriculoDisciplina",
            "periodo": _int(cd.periodo),
            "nivel": _int(cd.periodo),
            "tipo": _tipo_label(cd.tipo),
            "tipoCodigo": cd.tipo,
            "disciplina": {"resourceType": "Disciplina", "id": disc.id, "nome": disc.nome},
        }
        for cd, disc in linhas
    ]
    extra = ""
    if nivel is not None:
        extra += f"nivel={nivel}&"
    if tipo:
        extra += f"tipo={tipo}&"
    return search_set(
        items, len(items), 0, len(items) or 1, f"/api/Curriculo/{id}/disciplinas", extra
    )


@router.post("/{id}/disciplinas", status_code=status.HTTP_201_CREATED)
async def add_disciplina_to_curriculo(id: str, disc_in: CurriculoDisciplinaCreate, db: AsyncSession = Depends(get_db)):
    """Vincula uma disciplina como componente do currículo (SIGAA_RL_CURRICULO_DISCIPLINA)."""
    await add_disciplina(db, _db_id(id), disc_in)
    return {
        "resourceType": "CurriculoDisciplina",
        "curriculo": id,
        "disciplina": disc_in.disciplina,
        "periodo": disc_in.periodo,
        "nivel": disc_in.periodo,
        "tipo": _tipo_label(disc_in.tipo),
        "tipoCodigo": disc_in.tipo,
    }
