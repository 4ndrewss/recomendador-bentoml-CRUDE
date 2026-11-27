"""Resumo do registro de chamadas (log_dados.jsonl)."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from acesso_dados import carregar_catalogo
from registro import ARQUIVO_LOG


def _ler_texto(caminho: Path) -> str:
    """Lê o arquivo tratando UTF-8 (com ou sem BOM) e UTF-16 (PowerShell)."""
    bruto = caminho.read_bytes()
    if bruto.startswith((b"\xff\xfe", b"\xfe\xff")):
        return bruto.decode("utf-16")
    return bruto.decode("utf-8-sig")


def ler_log(caminho: Path) -> tuple[list[dict], int]:
    """Lê as linhas JSON válidas do arquivo de log e conta linhas inválidas."""
    linhas: list[dict] = []
    invalidas = 0
    for texto in _ler_texto(caminho).splitlines():
        texto = texto.strip()
        if not texto:
            continue
        try:
            item = json.loads(texto)
        except json.JSONDecodeError:
            invalidas += 1
            continue
        if isinstance(item, dict):
            linhas.append(item)
        else:
            invalidas += 1
    return linhas, invalidas


def montar_resumo(caminho: Path = ARQUIVO_LOG) -> str:
    """Gera o texto de resumo do arquivo de log sem falhar se ausente ou vazio."""
    if not caminho.exists():
        return f"Arquivo de log não encontrado: {caminho.name} (nenhuma chamada registrada ainda)."

    linhas, invalidas = ler_log(caminho)
    if not linhas:
        aviso = f" ({invalidas} linha(s) inválida(s) ignorada(s))" if invalidas else ""
        return f"O arquivo {caminho.name} está vazio - 0 chamadas registradas{aviso}."

    produtos = {p["id"]: p for p in carregar_catalogo()["produtos"]}

    por_funcao: Counter[str] = Counter()
    erros_por_motivo: Counter[str] = Counter()
    uso_catalogo: Counter[str] = Counter()
    fora_catalogo: Counter[str] = Counter()
    total_erros = 0

    for linha in linhas:
        por_funcao[str(linha.get("funcao") or "desconhecida")] += 1

        sucesso = linha.get("sucesso", True)
        motivo_erro = linha.get("erro")
        if not sucesso or motivo_erro is not None:
            total_erros += 1
            erros_por_motivo[str(motivo_erro or "erro_desconhecido")] += 1

        # set evita contar o mesmo id duas vezes numa única chamada
        # (ex.: buscar_produto recebe ["p01"] em identificadores e devolve ["p01"] em retornados).
        identificadores = linha.get("identificadores") or []
        retornados = linha.get("retornados") or []
        ids_da_chamada = {
            str(pid) for pid in (*identificadores, *retornados) if pid is not None and str(pid)
        }
        for pid in ids_da_chamada:
            if pid in produtos:
                uso_catalogo[pid] += 1
            else:
                fora_catalogo[pid] += 1

    total_chamadas = len(linhas)
    total_sucesso = total_chamadas - total_erros

    saida = [
        f"=== Resumo do registro ({caminho.name}) ===",
        f"Total de chamadas: {total_chamadas} ({total_sucesso} com sucesso, {total_erros} com erro)",
    ]
    if invalidas:
        saida.append(f"Linhas inválidas ignoradas: {invalidas}")

    saida.append("")
    saida.append("Chamadas por função:")
    for funcao, qtd in sorted(por_funcao.items(), key=lambda x: (-x[1], x[0])):
        saida.append(f"  - {funcao}: {qtd}")

    saida.append("")
    saida.append(f"Erros: {total_erros}")
    for motivo, qtd in sorted(erros_por_motivo.items(), key=lambda x: (-x[1], x[0])):
        saida.append(f"  - {motivo}: {qtd}")

    saida.append("")
    total_catalogo = len(produtos)
    if uso_catalogo:
        ordenados = sorted(uso_catalogo.items(), key=lambda x: (-x[1], x[0]))
        saida.append(
            f"Produtos consultados ({len(ordenados)} de {total_catalogo} do catálogo, "
            "contando pedidos e retornados):"
        )
        for pid, qtd in ordenados:
            nome = produtos[pid]["nome"]
            saida.append(f"  - {pid} ({nome}): {qtd} chamada(s)")

        maior = ordenados[0][1]
        menor = ordenados[-1][1]
        mais_usados = [pid for pid, qtd in ordenados if qtd == maior]
        menos_usados = [pid for pid, qtd in ordenados if qtd == menor]

        saida.append(f"  Mais consultado(s): {', '.join(mais_usados)} ({maior} chamada(s))")
        if menor < maior:
            saida.append(
                f"  Menos consultado(s) entre os usados: {', '.join(menos_usados)} ({menor} chamada(s))"
            )
    else:
        saida.append(f"Produtos consultados: nenhum dos {total_catalogo} produtos do catálogo.")

    nunca_usados = [pid for pid in sorted(produtos) if pid not in uso_catalogo]
    saida.append("")
    saida.append(f"Produtos nunca usados ({len(nunca_usados)} de {total_catalogo}):")
    if nunca_usados:
        for pid in nunca_usados:
            produto = produtos[pid]
            sufixo = " [estoque: 0]" if produto.get("estoque", 0) == 0 else ""
            saida.append(f"  - {pid} ({produto['nome']}){sufixo}")
    else:
        saida.append("  - Nenhum (todos os produtos do catálogo foram usados).")

    if fora_catalogo:
        saida.append("")
        saida.append("IDs fora do catálogo consultados:")
        for pid, qtd in sorted(fora_catalogo.items(), key=lambda x: (-x[1], x[0])):
            saida.append(f"  - {pid}: {qtd} chamada(s)")

    return "\n".join(saida)


def main() -> None:
    caminho = Path(sys.argv[1]) if len(sys.argv) > 1 else ARQUIVO_LOG
    print(montar_resumo(caminho))


if __name__ == "__main__":
    main()
