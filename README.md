# 🏺 Projeto Origem — Módulo de Recomendação
> **Primeiro, leia o [SETUP.md](SETUP.md)** para instalar e testar o projeto.

## 🪪 Identificação

- **Projeto:** Origem
- **Grupo:** CRUDE
- **Turma:** ADS Regular (Turma A) — CESAR School
- **Membros:**
  - Andrews Queiroz
  - Arthur Marques
  - Caio Gilles
  - Enzo Barbosa
  - Gustavo Veloso
  - Pedro Henrique

---

## 🔎 O que é

Mockup do módulo de recomendação do projeto **Origem**, desenvolvido com BentoML e estruturado a partir dos requisitos da **AV1**. 

O serviço atua como um sistema de ranqueamento que sugere itens artesanais similares a partir da página do produto visualizado pelo comprador, priorizando mesma técnica artesanal e mesma região geográfica. A solução integra regras de negócio para omissão automática de produtos indisponíveis em estoque e ordenação por relevância combinando popularidade e co-ocorrência em compras.

---

## ⚙️ Como instalar e subir

Para instruções detalhadas de ambiente, pré-requisitos e resolução de problemas, consulte o **[SETUP.md](SETUP.md)**.

Em resumo, execute na raiz do repositório:

```bash
uv run python treino.py
uv run bentoml serve service:Recomendador
```

O serviço fica em `http://127.0.0.1:3000` (Swagger interativo disponível na mesma URL).

---

## 🔄️ Mapeamento de Requisitos Funcionais (AV1)

| RF | Descrição | Endpoint | Status |
| :--- | :--- | :--- | :--- |
| **RF-01** | Recomendação por técnica similar | `POST /api/v1/recomendacoes` | Implementado |
| **RF-02** | Recomendação por região de origem | `POST /api/v1/recomendacoes` | Implementado |
| **RF-05** | Omitir produtos sem estoque | `POST /api/v1/recomendacoes` | Implementado |
| **RF-03** | Recomendação personalizada na tela inicial | — | Fora do mockup |
| **RF-04** | Sugestão de perfis de artesãos | — | Fora do mockup |

> **Nota sobre o protocolo HTTP:** A especificação original da AV1 define o método `GET` para a rota de recomendações, mas como o framework BentoML trabalha nativamente com `POST` para requisições de serviço com payload estruturado, este mockup expõe a rota `/api/v1/recomendacoes` utilizando o método `POST`.

---

## 📥 Entrada e Saída

### Contrato do Endpoint (`POST /api/v1/recomendacoes`)

#### Campos de Entrada (JSON Body)

- `produto_id` *(string, obrigatório)*: Identificador único do produto que o usuário está visualizando no momento (ex.: `"p01"`).
- `usuario_id` *(string, opcional)*: Identificador do comprador logado na plataforma (campo aceito no payload e ignorado pelas regras do mockup).
- `limite` *(integer, opcional)*: Quantidade máxima de produtos sugeridos a retornar, com intervalo válido de 1 a 5 (padrão: `5`).

#### Campos de Saída (JSON Response)

- `status` *(string)*: Estado da resposta (`"sucesso"` ou `"erro"`).
- `recomendacoes` *(array de objetos)*: Lista ordenada dos produtos recomendados, contendo:
  - `produto_id` *(string)*: Identificador do produto recomendado.
  - `nome` *(string)*: Nome da peça artesanal.
  - `tecnica` *(string)*: Classificação da técnica artesanal.
  - `regiao` *(string)*: Polo cultural ou região geográfica de origem.
  - `artesao_id` *(string)*: Identificador do artesão produtor.
  - `nome_artesao` *(string)*: Nome do artesão responsável pela peça.
  - `score_relevancia` *(float)*: Pontuação de relevância atribuída pelo algoritmo.
  - `motivo` *(string)*: Justificativa da sugestão (`"mesma_tecnica"` ou `"mesma_regiao"`).

#### Tratamento de Erros

- **`HTTP 400 Bad Request`**: Retornado caso os parâmetros de entrada sejam inválidos (por exemplo, `limite` fora do intervalo de 1 a 5).
- **`HTTP 404 Not Found`**: Retornado quando o `produto_id` informado não existir no catálogo.

### Exemplo de Uso

#### Requisição via cURL / Terminal:

```bash
curl -X POST http://127.0.0.1:3000/api/v1/recomendacoes \
  -H "Content-Type: application/json" \
  -d '{"produto_id": "p01", "limite": 3}'
```

#### Requisição via PowerShell:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:3000/api/v1/recomendacoes" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"produto_id": "p01", "limite": 3}' | ConvertTo-Json -Depth 5
```

#### Exemplo de Resposta (`200 OK`):

```json
{
  "status": "sucesso",
  "recomendacoes": [
    {
      "produto_id": "p03",
      "nome": "Boneca de barro",
      "tecnica": "ceramica",
      "regiao": "Tracunhaém",
      "artesao_id": "a02",
      "nome_artesao": "José Ferreira",
      "score_relevancia": 0.8083,
      "motivo": "mesma_tecnica"
    },
    {
      "produto_id": "p04",
      "nome": "Moringa de barro",
      "tecnica": "ceramica",
      "regiao": "Tracunhaém",
      "artesao_id": "a02",
      "nome_artesao": "José Ferreira",
      "score_relevancia":  0.775,
      "motivo": "mesma_tecnica"
    }
  ]
}
```
> Apesar de limite: 3, vieram apenas 2 itens: o p02 (mesma técnica) está sem estoque e é omitido pelo RF-05.

---

## 🎛️ Casos de teste

Com o serviço rodando (`uv run bentoml serve service:Recomendador`), execute em **outro terminal**. Os exemplos usam PowerShell; no Linux/Mac, use o `curl` equivalente do exemplo de uso acima.

### Teste 1 — RF-01: mesma técnica

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:3000/api/v1/recomendacoes" -Method Post -ContentType "application/json" -Body '{"produto_id": "p07"}' | ConvertTo-Json -Depth 5
```

**Esperado:** `status: "sucesso"` e 2 itens, ambos com `motivo: "mesma_tecnica"`:

| produto_id | score_relevancia |
| :--- | :--- |
| p08 | 0.7667 |
| p09 | 0.7167 |

### Teste 2 — RF-02: mesma região

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:3000/api/v1/recomendacoes" -Method Post -ContentType "application/json" -Body '{"produto_id": "p12"}' | ConvertTo-Json -Depth 5
```

**Esperado:** `status: "sucesso"` e 2 itens, ambos com `motivo: "mesma_regiao"` (o `p12` é o único de "madeira", então não há itens de mesma técnica):

| produto_id | score_relevancia |
| :--- | :--- |
| p10 | 0.2583 |
| p11 | 0.1417 |

### Teste 3 — RF-05: produto sem estoque não aparece

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:3000/api/v1/recomendacoes" -Method Post -ContentType "application/json" -Body '{"produto_id": "p01"}' | ConvertTo-Json -Depth 5
```

**Esperado:** `status: "sucesso"` e 2 itens com `motivo: "mesma_tecnica"`: `p03` (0.8083) e `p04` (0.775). O `p02` é da mesma técnica, mas está com estoque 0, então **não** aparece.

---

Baseado em [lgallindo/recomendador-bentoml](https://github.com/lgallindo/recomendador-bentoml)
