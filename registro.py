"""Registro (log) das chamadas de acesso_dados.py. Só acrescenta, nunca apaga."""

import functools
import inspect
import json
from datetime import datetime
from pathlib import Path

ARQUIVO_LOG = Path(__file__).resolve().parent / "log_dados.jsonl"


def _escrever_linha(linha: dict) -> None:
    # "a" = acrescentar no fim. Nunca usar "w", que apagaria as linhas antigas.
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(linha, ensure_ascii=False) + "\n")


def _contar(resultado) -> int:
    if resultado is None:
        return 0
    if isinstance(resultado, (list, tuple, set)):
        return len(resultado)
    return 1  # um único produto (dict)

def _ids(resultado) -> list[str]:
    if resultado is None:
        return []
    itens = resultado if isinstance(resultado, (list, tuple, set)) else [resultado]
    return [i["id"] for i in itens if isinstance(i, dict) and "id" in i]


def registrar(produto_existe=None):
    """Decorador que anota cada chamada em log_dados.jsonl.

    produto_existe: função opcional (produto_id -> bool), usada quando a função
    devolve lista vazia e a gente precisa saber se o produto existe mesmo.
    """

    def decorador(func):
        assinatura = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            argumentos = assinatura.bind(*args, **kwargs)
            argumentos.apply_defaults()
            produto_id = argumentos.arguments.get("produto_id")
            chamador = argumentos.arguments.get("chamador") or "desconhecido"

            linha = {
                "data_hora": datetime.now().isoformat(timespec="seconds"),
                "funcao": func.__name__,
                "chamador": chamador,
                "identificadores": [produto_id],  # só o id, nunca o produto inteiro
                "quantidade": 0,
                "retornados": [],
                "sucesso": True,
                "erro": None,
            }

            try:
                resultado = func(*args, **kwargs)
                linha["quantidade"] = _contar(resultado)
                linha["retornados"] = _ids(resultado)

                nao_achou = resultado is None or (
                    produto_existe is not None
                    and not resultado
                    and not produto_existe(produto_id)
                )
                if nao_achou:
                    linha["sucesso"] = False
                    linha["erro"] = "produto_nao_encontrado"
                return resultado
            except Exception as e:
                linha["sucesso"] = False
                linha["erro"] = type(e).__name__  # só o tipo, sem dado dentro da mensagem
                raise
            finally:
                try:
                    _escrever_linha(linha)
                except OSError:
                    pass  # se o log falhar, a função principal continua normal

        return wrapper

    return decorador