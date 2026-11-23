"""Leitura do catálogo e consultas usadas pelo recomendador."""

import json
from pathlib import Path


DADOS = Path(__file__).resolve().parent / "dados" / "catalogo.json"


def carregar_catalogo() -> dict:
    """Carrega os produtos e as cestas usados para gerar o modelo."""
    return json.loads(DADOS.read_text(encoding="utf-8"))


def buscar_produto(produto_id: str, produtos: dict[str, dict]) -> dict | None:
    """Busca o produto pelo ID ou retorna None quando ele não existe."""
    return produtos.get(produto_id)


def listar_produtos_parecidos(
    produto: dict,
    produtos: dict[str, dict],
    *,
    incluir_mesma_regiao: bool = False,
) -> list[dict]:
    """Lista outros produtos em estoque da mesma técnica, a categoria do catálogo.

    Se solicitado, também inclui produtos da mesma região. Retorna uma lista
    vazia quando não há candidatos.
    """
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
