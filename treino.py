"""Lê o catálogo, calcula popularidade e co-ocorrência, guarda no BentoML."""

from __future__ import annotations

import pickle
from collections import defaultdict
from pathlib import Path

import bentoml

from acesso_dados import carregar_catalogo

ARTEFATO = "model.pkl"


def _cooc(cestas: list[list[str]]) -> dict[str, dict[str, float]]:
    """Quantas vezes dois produtos aparecem juntos nas cestas de exemplo."""
    conta: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for cesta in cestas:
        ids = list(dict.fromkeys(cesta))
        for i, a in enumerate(ids):
            for b in ids[i + 1 :]:
                conta[a][b] += 1.0
                conta[b][a] += 1.0
    cooc: dict[str, dict[str, float]] = {}
    for a, vizinhos in conta.items():
        m = max(vizinhos.values()) if vizinhos else 1.0
        cooc[a] = {b: v / m for b, v in vizinhos.items()}
    return cooc


def main() -> None:
    catalogo = carregar_catalogo()
    produtos = {p["id"]: p for p in catalogo["produtos"]}
    pedidos_brutos = {pid: float(p["pedidos"]) for pid, p in produtos.items()}
    max_pedidos = max(pedidos_brutos.values(), default=1.0) or 1.0
    pop = {pid: n / max_pedidos for pid, n in pedidos_brutos.items()}
    cooc = _cooc(catalogo["cestas"])

    artefato = {
        "produtos": produtos,
        "pedidos_brutos": pedidos_brutos,
        "pop": pop,
        "cooc": cooc,
        "estrategia": "mesma_tecnica_mais_pedidos",
    }

    with bentoml.models.create(
        "recomendador",
        labels={"aula": "recomendador-bentoml", "regra": "tecnica+pedidos"},
        metadata={
            "n_produtos": len(produtos),
            "n_cestas": len(catalogo["cestas"]),
            "estrategia": artefato["estrategia"],
        },
    ) as model:
        Path(model.path_of(ARTEFATO)).write_bytes(pickle.dumps(artefato))
        tag = model.tag

    print(f"produtos no catálogo  {len(produtos)}")
    print(f"tag no store          {tag}")


if __name__ == "__main__":
    main()
