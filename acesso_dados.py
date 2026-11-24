"""Leitura do catálogo e consultas usadas pelo recomendador."""

import json
from pathlib import Path

from registro import registrar


DADOS = Path(__file__).resolve().parent / "dados" / "catalogo.json"


def carregar_catalogo() -> dict:
    """Carrega os produtos e as cestas usados para gerar o modelo."""
    return json.loads(DADOS.read_text(encoding="utf-8"))


def _produtos_por_id() -> dict[str, dict]:
    """Lê o catálogo e devolve os produtos indexados pelo id."""
    return {p["id"]: p for p in carregar_catalogo()["produtos"]}


def _produto_existe(produto_id: str) -> bool:
    return produto_id in _produtos_por_id()


@registrar()
def buscar_produto(produto_id: str, *, chamador: str | None = None) -> dict | None:
    """Busca o produto pelo ID ou retorna None quando ele não existe."""
    return _produtos_por_id().get(produto_id)


@registrar(produto_existe=_produto_existe)
def listar_produtos_parecidos(
    produto_id: str,
    *,
    incluir_mesma_regiao: bool = False,
    chamador: str | None = None,
) -> list[dict]:
    """Lista outros produtos em estoque da mesma técnica, a categoria do catálogo.

    Se solicitado, também inclui produtos da mesma região. Retorna uma lista
    vazia quando o produto não existe ou não há candidatos.
    """
    produtos = _produtos_por_id()
    produto = produtos.get(produto_id)
    if produto is None:
        return []
    return [
        candidato
        for candidato in produtos.values()
        if candidato["id"] != produto["id"]
        and candidato.get("estoque", 0) > 0
        and (
            candidato["tecnica"] == produto["tecnica"]
            or (incluir_mesma_regiao and candidato["regiao"] == produto["regiao"])
        )
    ]