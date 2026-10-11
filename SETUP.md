# 🖥️ Setup (Windows: PowerShell ou Git Bash)

Guia para instalar e testar o serviço. Se algo falhar, veja a seção **Problemas comuns**.

Use o **PowerShell** pra instalar (passo 1). Nos passos 2 a 4, serve **PowerShell ou Git Bash**. **Não use o CMD**: os comandos deste guia não foram feitos pra ele.

## 1. Pré-requisitos

| Programa | Para quê | Instalação |
| --- | --- | --- |
| Git | clonar o repo | https://git-scm.com |
| uv | gerencia Python e dependências | `winget install --id astral-sh.uv -e` |
| just *(opcional)* | atalhos de comando | `winget install --id Casey.Just --exact` |
| Python 3.13 | roda o projeto | instalado automaticamente pelo uv (não precisa instalar) |

- Depois de instalar, **feche e abra o terminal** (se for VS Code, feche o VS Code inteiro).
- Confira: `uv --version` (e `just --version`, se instalou)

## 2. Clonar

```bash
git clone https://github.com/4ndrewss/recomendador-bentoml-CRUDE.git # link do repo
cd recomendador-bentoml-CRUDE # pasta do repo
```

## 3. Treinar e subir

1. Treine o modelo (rode de novo sempre que mudar o `catalogo.json`):
```
   uv run python treino.py
```
2. Suba o serviço:
```
   uv run bentoml serve service:Recomendador
```

O serviço fica em http://127.0.0.1:3000 (Swagger na mesma URL). O terminal fica ocupado até você apertar `Ctrl+C`, e isso é normal: abra **outro terminal** pra testar.

Na primeira execução o `uv` baixa Python e dependências, então pode demorar. Se você tem o `just`, `just treino` e `just serve` fazem o mesmo.

## 4. Testar (em outro terminal)

PowerShell:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:3000/api/v1/recomendacoes -Method Post -ContentType "application/json" -Body '{"produto_id":"p01","limite":3}' | ConvertTo-Json -Depth 5
```

Git Bash:

```bash
curl -X POST http://127.0.0.1:3000/api/v1/recomendacoes -H "Content-Type: application/json" -d '{"produto_id":"p01","limite":3}'
```

Se retornar `status: "sucesso"` com `p03` e `p04` em `recomendacoes`, o setup está ok.

## 💥 Problemas comuns

**`just` / `uv` "não é reconhecido como cmdlet" (PowerShell)**- 
O terminal não enxerga o programa (PATH). Feche e abra o terminal. Se persistir:

```
winget list --id Casey.Just
Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter just.exe | Select-Object FullName
```

Adicione a pasta encontrada ao PATH da sessão:

```
$env:Path += ";<PASTA-ONDE-ESTÁ-O-EXE>"
```

**`just.exe` bloqueado: "Uma política de Controle de Aplicativo bloqueou este arquivo"**- 
Comum em PCs de faculdade/trabalho. Não tente burlar a política. Use os comandos `uv run ...` do passo 3 (o `just` é só atalho).

**Windows avisa "comando potencialmente perigoso" ao instalar o uv**- 
O instalador `irm ... | iex` dispara esse alerta. Use `winget install --id astral-sh.uv -e`.

**`curl` dá "Invalid JSON (PowerShell): key must be a string"**- 
O PowerShell estraga as aspas do `curl.exe -d`. Use `Invoke-RestMethod` (passo 4) ou o Swagger em http://127.0.0.1:3000.

**Porta 3000 ocupada**- 
Feche outro `serve` ou container rodando e tente de novo.
