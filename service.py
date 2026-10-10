"""Serve recomendações do Origem (contrato AV1): mesma técnica e mesma região, só com estoque."""

from __future__ import annotations

import pickle
from pathlib import Path

import bentoml

modelo = bentoml.models.get("recomendador:latest")
ARTEFATO = "model.pkl"
LIMITE_MAXIMO = 5


@bentoml.service(resources={"cpu": "1"})
class Recomendador:

    def __init__(self) -> None:
        caminho = Path(modelo.path_of(ARTEFATO))
        self.artefato = pickle.loads(caminho.read_bytes())

    @bentoml.api(route="/api/v1/recomendacoes")
    def recomendacoes(
        self,
        ctx: bentoml.Context,
        produto_id: str,
        usuario_id: str | None = None,
        limite: int = LIMITE_MAXIMO,
    ) -> dict:
        """Devolve outros produtos a partir do produto que o cliente está vendo.

        Entrada:
          - produto_id: id do produto aberto na tela (ex.: \"p01\")
          - usuario_id: aceito e ignorado (mockup)
          - limite: quantos produtos sugerir, de 1 a 5 (padrão 5)

        Regras:
          - RF-01: produtos da mesma técnica (motivo \"mesma_tecnica\")
          - RF-02: produtos da mesma região (motivo \"mesma_regiao\")
          - RF-05: nunca devolve produto sem estoque
          - o próprio produto_id nunca entra nas sugestões

        Erros: limite fora de 1..5 → 400; produto_id inexistente → 404.
        """
        if not 1 <= limite <= LIMITE_MAXIMO:
            ctx.response.status_code = 400
            return {
                "status": "erro",
                "mensagem": f"limite deve estar entre 1 e {LIMITE_MAXIMO}",
                "recomendacoes": [],
            }

        produtos = self.artefato["produtos"]
        if produto_id not in produtos:
            ctx.response.status_code = 404
            return {
                "status": "erro",
                "mensagem": f"produto {produto_id} não encontrado",
                "recomendacoes": [],
            }

        atual = produtos[produto_id]
        pop = self.artefato["pop"]
        pedidos_brutos = self.artefato["pedidos_brutos"]
        cooc_pagina = self.artefato["cooc"].get(produto_id, {})

        candidatos = []
        for pid, p in produtos.items():
            if pid == produto_id or p.get("estoque", 0) <= 0:
                continue
            if p["tecnica"] == atual["tecnica"]:
                motivo = "mesma_tecnica"
            elif p["regiao"] == atual["regiao"]:
                motivo = "mesma_regiao"
            else:
                continue
            base = 0.7 * pop[pid] + 0.3 * cooc_pagina.get(pid, 0.0)
            # Faixas separadas: técnica fica em 0.5–1.0 e região em 0.0–0.5,
            # então quem tem a mesma técnica aparece antes.
            score = 0.5 + 0.5 * base if motivo == "mesma_tecnica" else 0.5 * base
            candidatos.append((score, pid, motivo))

        candidatos.sort(key=lambda c: (c[0], pedidos_brutos[c[1]]), reverse=True)

        recomendacoes = []
        for score, pid, motivo in candidatos[:limite]:
            p = produtos[pid]
            recomendacoes.append(
                {
                    "produto_id": pid,
                    "nome": p["nome"],
                    "tecnica": p["tecnica"],
                    "regiao": p["regiao"],
                    "artesao_id": p["artesao_id"],
                    "nome_artesao": p["nome_artesao"],
                    "score_relevancia": round(score, 4),
                    "motivo": motivo,
                }
            )

        return {"status": "sucesso", "recomendacoes": recomendacoes}
