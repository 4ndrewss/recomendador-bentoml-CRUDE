# 🏺 Origem — Projeto Final (Grupo CRUDE)

> **Rascunho.** Os trechos marcados com `TODO` ainda precisam ser preenchidos pelo grupo.

Serviço de recomendação do marketplace **Origem**, feito com BentoML. A partir do produto que o cliente está vendo, a rota `POST /api/v1/recomendacoes` sugere outros produtos **da mesma técnica** ou, se não houver, **da mesma região**, e nunca sugere produto sem estoque.

Neste projeto final, todo acesso aos dados passa por funções próprias ([`acesso_dados.py`](acesso_dados.py)) e cada chamada fica anotada num registro ([`log_dados.jsonl`](#4-como-gerar-o-registro-com-3-chamadas-repetíveis)).

**Grupo CRUDE** (ADS Regular, Turma A, CESAR School): Andrews Queiroz, Arthur Marques, Caio Gilles, Enzo Barbosa, Gustavo Veloso e Pedro Henrique.

## Sumário

1. [Como instalar e rodar](#1-como-instalar-e-rodar)
2. [Dicionário de dados](#2-dicionário-de-dados)
3. [Funções de acesso](#3-funções-de-acesso)
4. [Como gerar o registro com 3 chamadas repetíveis](#4-como-gerar-o-registro-com-3-chamadas-repetíveis)
5. [Como ver o resumo](#5-como-ver-o-resumo)
6. [Respostas (a), (b) e (c)](#6-respostas-a-b-e-c)
7. [Experimento: mudei um dado, a resposta mudou](#7-experimento-mudei-um-dado-a-resposta-mudou)
8. [Declaração de uso de IA generativa](#8-declaração-de-uso-de-ia-generativa)
9. [Conferências finais](#9-conferências-finais)

---

## 1. Como instalar e rodar

Detalhes e problemas comuns estão no [SETUP.md](SETUP.md). Resumo para Windows (PowerShell):

**Pré-requisitos** (instale uma vez, depois feche e abra o terminal):

```powershell
winget install --id astral-sh.uv -e
winget install --id Casey.Just --exact   # opcional, só atalhos
```

**Clonar, treinar e subir:**

```powershell
git clone https://github.com/4ndrewss/recomendador-bentoml-CRUDE.git
cd recomendador-bentoml-CRUDE
just treino        # ou: uv run python treino.py
just serve         # ou: uv run bentoml serve service:Recomendador
```

O serviço fica em http://127.0.0.1:3000 (com Swagger na mesma URL). Deixe esse terminal aberto e use **outro terminal** para os testes.

## 2. Dicionário de dados

Os dados ficam em [`dados/catalogo.json`](dados/catalogo.json), com duas listas: `produtos` (12 produtos de artesanato pernambucano) e `cestas` (8 compras de exemplo). A versão completa está em [dicionario_de_dados.md](dicionario_de_dados.md).

| Campo | Onde | Tipo | Significado |
| :--- | :--- | :--- | :--- |
| `id` | produto | texto | Identificador único (`p01` a `p12`) |
| `nome` | produto | texto | Nome exibido no catálogo |
| `tecnica` | produto | texto | `ceramica`, `renda`, `cestaria`, `xilogravura` ou `madeira` |
| `regiao` | produto | texto | Tracunhaém, Pesqueira, Agreste Pernambucano ou Bezerros |
| `pedidos` | produto | inteiro | Quantos pedidos o produto já teve (popularidade) |
| `estoque` | produto | inteiro | Unidades disponíveis; com `0` o produto não é recomendado |
| `artesao_id` | produto | texto | Identificador do artesão (ex.: `a02`) |
| `nome_artesao` | produto | texto | Nome do artesão (**fictício**) |
| `cestas` | raiz | lista de listas | Ids comprados juntos; geram a co-ocorrência no treino |

## 3. Funções de acesso

Todas em [`acesso_dados.py`](acesso_dados.py). A rota não abre o arquivo diretamente: ela usa só as funções públicas abaixo.

| Função | O que faz | Retorno | Registrada no log? |
| :--- | :--- | :--- | :--- |
| `carregar_catalogo()` | Lê o `catalogo.json` inteiro (usada pelo treino) | `dict` com `produtos` e `cestas` | Não |
| `buscar_produto(produto_id, *, chamador)` | Busca um produto pelo id | o produto (`dict`) ou `None` | Sim |
| `listar_produtos_parecidos(produto_id, *, incluir_mesma_regiao, chamador)` | Lista outros produtos **com estoque** da mesma técnica e, se pedido, da mesma região | lista de produtos (vazia se o id não existe) | Sim |

O registro é feito pelo decorador `@registrar()` em [`registro.py`](registro.py). Cada chamada acrescenta uma linha em `log_dados.jsonl` com os campos `data_hora`, `funcao`, `chamador`, `identificadores`, `quantidade`, `retornados`, `sucesso` e `erro`. O decorador só acrescenta linhas, nunca apaga, e grava apenas ids, nunca o produto inteiro.

A rota passa `chamador="rota"`, então dá para separar no log as chamadas da API das chamadas de teste.

## 4. Como gerar o registro com 3 chamadas repetíveis

Com o serviço rodando (seção 1), no segundo terminal:

```powershell
just curl-exemplo       # p01, produto normal         → p03 e p04
just curl-complemento   # p12, sem mesma técnica      → p10 e p11 (mesma região)
just curl-inexistente   # id que não existe           → HTTP 404
Get-Content log_dados.jsonl -Encoding utf8 -Tail 5
```

Sem o `just`, use os comandos `Invoke-RestMethod` da seção "Casos de teste" do [README.md](README.md).

Linhas esperadas no fim do `log_dados.jsonl` (o horário muda):

```json
{"funcao": "buscar_produto", "chamador": "rota", "identificadores": ["p01"], "quantidade": 1, "retornados": ["p01"], "sucesso": true, "erro": null}
{"funcao": "listar_produtos_parecidos", "chamador": "rota", "identificadores": ["p01"], "quantidade": 2, "retornados": ["p03", "p04"], "sucesso": true, "erro": null}
{"funcao": "buscar_produto", "chamador": "rota", "identificadores": ["p12"], "quantidade": 1, "retornados": ["p12"], "sucesso": true, "erro": null}
{"funcao": "listar_produtos_parecidos", "chamador": "rota", "identificadores": ["p12"], "quantidade": 2, "retornados": ["p10", "p11"], "sucesso": true, "erro": null}
{"funcao": "buscar_produto", "chamador": "rota", "identificadores": ["nao-existe"], "quantidade": 0, "retornados": [], "sucesso": false, "erro": "produto_nao_encontrado"}
```

**3 linhas que mostram o uso dos dados:**

1. A 2ª linha mostra que a rota consultou o catálogo a partir de `p01` e usou `p03` e `p04`. O `p02` não aparece porque está sem estoque.
2. A 4ª linha mostra que, para `p12`, a rota usou produtos da mesma região (`p10`, `p11`).
3. A 5ª linha mostra que a rota procurou `nao-existe` no catálogo, não achou e parou ali (devolveu 404).

O `log_dados.jsonl` não vai para o git. Uma cópia gerada pelo grupo está em [evidencias/07-log-card04.txt](evidencias/07-log-card04.txt).

## 5. Como ver o resumo

> `TODO (card 05)`: comando para gerar o resumo do registro e um exemplo da saída.

```powershell
# TODO: ex.: uv run python resumo.py
```

## 6. Respostas (a), (b) e (c)

> `TODO (card 05)`: copiar as perguntas do enunciado e responder com base no resumo.

**(a)** TODO

**(b)** TODO

**(c)** TODO

## 7. Experimento: mudei um dado, a resposta mudou

O `p02` (Prato de barro esmaltado, cerâmica) começa com `estoque: 0` e por isso não aparece nas recomendações do `p01`.

1. Com o serviço rodando, rode `just curl-exemplo`. Vêm `p03` e `p04`.
2. Em [`dados/catalogo.json`](dados/catalogo.json), troque o `estoque` do `p02` de `0` para `3` e salve.
3. Rode `just curl-exemplo` de novo, **sem reiniciar o serviço**. Agora vêm `p02` (score 0.8833), `p03` e `p04`.
4. No log, a última linha de `listar_produtos_parecidos` passa a ter `"retornados": ["p02", "p03", "p04"]`.
5. Volte o `estoque` do `p02` para `0`.

**Por que funciona sem reiniciar:** as funções de acesso leem o `catalogo.json` a cada chamada. Já os scores (popularidade e co-ocorrência) vêm do modelo treinado. Se mudar `pedidos` ou `cestas`, rode `just treino` e reinicie o `just serve`.

## 8. Declaração de uso de IA generativa

> `TODO`: cada membro confere e completa a sua parte.

| Membro | Ferramenta | Para quê |
| :--- | :--- | :--- |
| Gustavo Veloso | Claude Code (Anthropic), no VS Code | Card 04: passar `chamador="rota"` na rota, rodar as 3 chamadas, fazer o experimento de estoque e documentar no README; rascunho deste README |
| Andrews Queiroz | TODO | TODO |
| Arthur Marques | TODO | TODO |
| Caio Gilles | TODO | TODO |
| Enzo Barbosa | TODO | TODO |
| Pedro Henrique | TODO | TODO |

Todo o conteúdo gerado com IA foi revisado e testado pelo grupo antes de entrar no repositório.

## 9. Conferências finais

- [x] **Sem pessoas reais:** os nomes de artesãos no catálogo são inventados, e não há dados de clientes.
- [x] **Sem chaves ou senhas:** o repositório não tem tokens, senhas ou arquivos `.env`.
- [x] **Tudo no repositório:** código, dados, dicionário, evidências e este README. Só ficam de fora o `.venv/`, o store do BentoML e o `log_dados.jsonl`, que são gerados ao rodar.
- [ ] **Teste final:** alguém de fora do grupo segue só este README, roda o serviço, faz as 3 chamadas, abre o registro e aponta as 3 linhas da seção 4. `TODO: quem testou e quando`.
