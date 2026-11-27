# 🏺 Origem — Projeto Final (Grupo CRUDE)

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
> Se o Windows bloquear o `bentoml` (erro de "Controle de Aplicativo"), use: `uv run python -m bentoml serve service:Recomendador`

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

**Casos difíceis incluídos de propósito:** o `p12` é a única peça de madeira (não tem semelhante da mesma técnica), o `p02` está com `estoque: 0` e o id `nao-existe` não está no catálogo.

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

O `log_dados.jsonl` não vai para o git. Uma cópia gerada pelo grupo está em [evidencias/07-log-card04.txt](evidencias/07-log-card04.txt): as 5 primeiras linhas são as 3 chamadas acima, e as 2 últimas vêm do experimento da seção 7 (estoque do `p02` trocado de 0 para 3, o que fez o `p02` aparecer nos retornados).

## 5. Como ver o resumo

Já existe um exemplo de saída do nosso resumo aqui: [`08-resumo-card05.txt`](evidencias/08-resumo-card05.txt).

Para gerar o seu, faça antes as 3 chamadas da [seção 4](#4-como-gerar-o-registro-com-3-chamadas-repetíveis) e depois rode:

```powershell
just resumo          # ou: uv run python resumo_log.py
```

## 6. Respostas (a), (b) e (c)

- **(a) Qual dado mais usa?** Nas 3 chamadas oficiais, a função mais acionada é `buscar_produto`, pois toda requisição valida primeiro se o produto existe antes de buscar semelhantes. Entre os produtos do catálogo, os mais consultados são `p01` e `p12`, presentes em 2 chamadas cada, seguidos por `p03`, `p04`, `p10` e `p11`. Assim, os dados mais utilizados pertencem às técnicas `ceramica`, `madeira` e `xilogravura`, das regiões de Tracunhaém e Bezerros.
- **(b) Algum nunca usado e o que isso sugere?** Sim: 6 dos 12 produtos (`p02`, `p05`, `p06`, `p07`, `p08` e `p09`) não apareceram nas 3 chamadas. O `p02` não aparece por estar com `estoque: 0` (regra RF-05). Os de renda e cestaria (`p05` a `p09`) não aparecem porque as 3 chamadas não pediram essas técnicas, ou seja, "nunca usado" aqui quer dizer "ainda não testado".
- **(c) Houve erro e por quê?** Sim, houve 1 erro registrado na função `buscar_produto`, com o motivo `produto_nao_encontrado`. Ele ocorreu na 3ª chamada oficial, que consultou o identificador inexistente `nao-existe`. Como o produto não foi encontrado, a rota interrompeu o fluxo com HTTP 404 e não chegou a acionar `listar_produtos_parecidos`.

## 7. Experimento: mudei um dado, a resposta mudou

O `p02` (Prato de barro esmaltado, cerâmica) começa com `estoque: 0` e por isso não aparece nas recomendações do `p01`.

1. Com o serviço rodando, rode `just curl-exemplo`. Vêm `p03` e `p04`.
2. Em [`dados/catalogo.json`](dados/catalogo.json), troque o `estoque` do `p02` de `0` para `3` e salve.
3. Rode `just curl-exemplo` de novo, **sem reiniciar o serviço**. Agora vêm `p02` (score 0.8833), `p03` e `p04`.
4. No log, a última linha de `listar_produtos_parecidos` passa a ter `"retornados": ["p02", "p03", "p04"]`.
5. Volte o `estoque` do `p02` para `0`.

**Por que funciona sem reiniciar:** as funções de acesso leem o `catalogo.json` a cada chamada. Já os scores (popularidade e co-ocorrência) vêm do modelo treinado. Se mudar `pedidos` ou `cestas`, rode `just treino` e reinicie o `just serve`.

## 8. Declaração de uso de IA generativa

O grupo usou duas ferramentas de IA generativa:

- **Claude** (Anthropic): divisão do trabalho em cards do Trello, conferência dos pull requests e do README, e orientação sobre testes e evidências.
- **Claude Code** (Anthropic): passar `chamador="rota"` na rota, rodar as 3 chamadas, fazer o experimento de estoque, documentar no README e escrever o rascunho deste README.

Todo o conteúdo gerado com IA foi revisado e testado pelo grupo antes de entrar no repositório.