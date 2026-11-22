# Baseline de recomendação no BentoML
#
# Dois momentos (não misture):
#   1) treino  — offline: lê JSON, grava modelo no store
#   2) serve   — online: carrega o modelo, responde HTTP
#
# Empacote (opcional, só o pipeline online):
#   treino → build (Bento) → containerize (imagem OCI) → serve-container
#
# Imagem de aula (tag estável): recomendador:aula
# Pare qualquer `just serve` na :3000 antes de `just serve-container`.

# No Windows o just usa PowerShell (o padrão dele é `sh`, que costuma não estar
# no PATH). Vale também para quem roda `just` dentro do Git Bash.
set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

# `just` sem argumentos lista as receitas (sem isso, rodaria `treino`).
default:
    @just --list

# ---------------------------------------------------------------------------
# Offline — treino
# ---------------------------------------------------------------------------

treino:
    # Lê dados/catalogo.json → calcula pop/cooc → store `recomendador:…`
    uv run python treino.py

# ---------------------------------------------------------------------------
# Online — processo local (sem Docker)
# ---------------------------------------------------------------------------

serve:
    # Requer `just treino` ao menos uma vez. Deixe o terminal aberto.
    uv run bentoml serve service:Recomendador --reload

# ---------------------------------------------------------------------------
# Empacote — Bento → imagem OCI → container
# ---------------------------------------------------------------------------
# O que entra no pacote está em bentofile.yaml:
#   service + *.py + dados/*.json + dep bentoml + modelo recomendador:latest
# O treino NÃO roda dentro do container; só a inferência.

build:
    # Congela o serviço num Bento (ainda não é imagem Docker).
    # Pré-requisito: `just treino` (senão falta recomendador:latest).
    uv run bentoml build

containerize:
    # Transforma o Bento `Recomendador:latest` numa imagem OCI.
    # --image-tag fixa o nome para a aula (evita decorar o hash do Bento).
    uv run bentoml containerize Recomendador:latest --image-tag recomendador:aula

# Atalho didático: Bento + imagem de uma vez (mesmos passos, na ordem).
imagem: build containerize

serve-container:
    # Sobe a imagem. Mesma API que `just serve` (porta 3000).
    # Pré-requisito: `just imagem` (ou build + containerize).
    docker run --rm -p 3000:3000 recomendador:aula serve

listar-bentos:
    # O que o `bentoml build` gravou no store de Bentos
    uv run bentoml list

listar-imagens:
    # A imagem que o `containerize` deixou no Docker local
    docker images recomendador

# ---------------------------------------------------------------------------
# Exemplos HTTP (serve local OU serve-container na :3000)
# Contrato: POST /api/v1/recomendacoes  { produto_id, limite }
# No Windows usa Invoke-RestMethod: `curl` no PowerShell é outro comando e
# estraga as aspas do JSON.
# ---------------------------------------------------------------------------

[windows]
curl-exemplo:
    # Cliente abriu o jarro de barro (p01) → esperado: p03 e p04 nas recomendações
    Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:3000/api/v1/recomendacoes' -ContentType 'application/json' -Body (@{ produto_id = 'p01'; limite = 3 } | ConvertTo-Json) | ConvertTo-Json -Depth 5

[unix]
curl-exemplo:
    # Cliente abriu o jarro de barro (p01) → esperado: p03 e p04 nas recomendações
    curl -sS -X POST http://127.0.0.1:3000/api/v1/recomendacoes \
      -H 'Content-Type: application/json' \
      -d '{"produto_id":"p01","limite":3}' | python3 -m json.tool

[windows]
curl-complemento:
    # p12 (madeira) não tem outro da mesma técnica → completa com a mesma região (Bezerros): p10 e p11
    Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:3000/api/v1/recomendacoes' -ContentType 'application/json' -Body (@{ produto_id = 'p12'; limite = 4 } | ConvertTo-Json) | ConvertTo-Json -Depth 5

[unix]
curl-complemento:
    # p12 (madeira) não tem outro da mesma técnica → completa com a mesma região (Bezerros): p10 e p11
    curl -sS -X POST http://127.0.0.1:3000/api/v1/recomendacoes \
      -H 'Content-Type: application/json' \
      -d '{"produto_id":"p12","limite":4}' | python3 -m json.tool

[windows]
curl-inexistente:
    # Produto que não existe → esperado: HTTP 404
    try { Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:3000/api/v1/recomendacoes' -ContentType 'application/json' -Body (@{ produto_id = 'nao-existe'; limite = 3 } | ConvertTo-Json) } catch { Write-Output ('HTTP ' + [int]$_.Exception.Response.StatusCode) }

[unix]
curl-inexistente:
    # Produto que não existe → esperado: HTTP 404
    curl -sS -i -X POST http://127.0.0.1:3000/api/v1/recomendacoes \
      -H 'Content-Type: application/json' \
      -d '{"produto_id":"nao-existe","limite":3}'

# ---------------------------------------------------------------------------
# Material de aula
# ---------------------------------------------------------------------------

slides:
    uv run python scripts/gerar_slides.py