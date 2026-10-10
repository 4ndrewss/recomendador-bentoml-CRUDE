# Setup (Windows / PowerShell)

Guia para instalar e testar o serviço. Se algo falhar, veja a seção **Problemas comuns**.

## 1. Pré-requisitos

| Programa | Para quê | Instalação |
| --- | --- | --- |
| Git | clonar o repo | https://git-scm.com |
| uv | gerencia Python e dependências | `winget install --id astral-sh.uv -e` |
| just *(opcional)* | atalhos de comando | `winget install --id Casey.Just --exact` |

- O Python 3.13 **não precisa** estar instalado: o `uv` baixa sozinho.
- Depois de instalar, **feche e abra o terminal** (se for VS Code, feche o VS Code inteiro).
- Confira: `uv --version` e `just --version`.

## 2. Clonar

```
git clone <LINK-DO-REPO>
cd <PASTA-DO-REPO>
```

## 3. Treinar e subir

Com `just`:

```
just treino
just serve
```

Sem `just` (equivalente, funciona em qualquer máquina):

```
uv run python treino.py
uv run bentoml serve service:Recomendador
```

Deixe o terminal do `serve` aberto. O serviço fica em http://127.0.0.1:3000 (Swagger na mesma URL).

> Na primeira execução o `uv` baixa Python e dependências. Pode demorar.

## 4. Testar (em outro terminal)

```
Invoke-RestMethod -Uri http://127.0.0.1:3000/recomendar -Method Post -ContentType "application/json" -Body '{"produto_na_pagina":"p01","limite":4,"excluir":[]}' | ConvertTo-Json -Depth 5
```

Se retornar `items` com sugestões, o setup está ok.

> Mudou o `dados/catalogo.json`? Rode o treino de novo e reinicie o serve.

## Problemas comuns

**`just` / `uv` "não é reconhecido como cmdlet"**
O terminal não enxerga o programa (PATH). Feche e abra o terminal. Se persistir:

```
winget list --id Casey.Just
Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter just.exe | Select-Object FullName
```

Adicione a pasta encontrada ao PATH da sessão:

```
$env:Path += ";<PASTA-ONDE-ESTÁ-O-EXE>"
```

**`just.exe` bloqueado: "Uma política de Controle de Aplicativo bloqueou este arquivo"**
Comum em PCs de faculdade/trabalho. Não tente burlar a política. Use os comandos `uv run ...` do passo 3 (o `just` é só atalho).

**Windows avisa "comando potencialmente perigoso" ao instalar o uv**
O instalador `irm ... | iex` dispara esse alerta. Use `winget install --id astral-sh.uv -e`.

**`curl` dá "Invalid JSON: key must be a string"**
O PowerShell estraga as aspas do `curl.exe -d`. Use `Invoke-RestMethod` (passo 4) ou o Swagger em http://127.0.0.1:3000.

**`p01` aparece na resposta, mas não nos `items`**
Normal: é o eco em `produto_na_pagina`. O produto da página nunca entra nas sugestões.

**Porta 3000 ocupada**
Feche outro `serve` ou container rodando e tente de novo.