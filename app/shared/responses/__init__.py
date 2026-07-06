"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Utilitário de resposta padronizada — envelope SearchSet.

Todas as listagens da API são serializadas neste envelope (padrão adotado a partir
da especificação do professor): total de registros, count/offset da página e links
HATEOAS (self/next/previous), além do array 'items' já com 'resourceType'.
"""
from typing import Any

from pydantic import BaseModel, Field


class SearchSet(BaseModel):
    """
    Modelo do envelope de listagem padronizado (SearchSet).

    Usado como `response_model` nos endpoints de pesquisa para que os contratos
    OpenAPI documentem explicitamente o formato da resposta (em vez de um schema
    vazio). Os itens são objetos livres, pois cada recurso carrega seu próprio
    conjunto de campos além da chave `resourceType`.
    """
    resourceType: str = Field(default="SearchSet", description="Tipo do recurso (sempre 'SearchSet')")
    total: int = Field(..., description="Total de registros que satisfazem o filtro")
    count: int = Field(..., description="Quantidade de itens nesta página")
    offset: int = Field(..., description="Deslocamento aplicado na paginação")
    link: dict[str, str] = Field(..., description="Links de navegação (self, next, previous)")
    items: list[dict[str, Any]] = Field(..., description="Itens da página (cada um com sua chave 'resourceType')")


def search_set(
    items: list[dict[str, Any]],
    total: int,
    offset: int,
    count: int,
    base_path: str,
    extra_query: str = "",
) -> dict[str, Any]:
    """
    Monta o envelope SearchSet para uma página de resultados.

    - items: itens já serializados (cada um com sua chave 'resourceType').
    - total: total de registros que satisfazem o filtro (não apenas a página).
    - offset/count: paginação aplicada.
    - base_path: caminho base do recurso (ex.: '/api/Aluno').
    - extra_query: parâmetros de filtro já formatados (ex.: 'nome=ada&') para
      preservar o filtro nos links de navegação.
    """
    def link(off: int) -> str:
        return f"{base_path}?{extra_query}_offset={off}&_count={count}"

    return {
        "resourceType": "SearchSet",
        "total": total,
        "count": len(items),
        "offset": offset,
        "link": {
            "self": link(offset),
            "next": link(offset + count) if offset + count < total else "",
            "previous": link(max(0, offset - count)) if offset > 0 else "",
        },
        "items": items,
    }
