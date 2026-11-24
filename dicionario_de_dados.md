# Dicionário de Dados — catalogo.json

O arquivo `catalogo.json` tem duas listas: `produtos` (12 itens do catálogo de artesanato pernambucano) e `cestas` (8 compras, cada uma com os produtos levados juntos).

## Campos

### `id`
Identificador único de cada produto, no formato `p01` a `p12`. É a chave usada para ligar um produto às cestas.

### `nome`
Nome do produto como aparece no catálogo (por exemplo, "Jarro de barro Tracunhaém"). É um texto livre, usado para exibição.

### `tecnica`
Técnica artesanal usada para fazer o produto. Pode ser `ceramica`, `renda`, `cestaria`, `xilogravura` ou `madeira`, o que permite agrupar os produtos por tipo de artesanato.

### `regiao`
Localidade de Pernambuco onde o produto é produzido: Tracunhaém, Pesqueira, Agreste Pernambucano ou Bezerros. Permite analisar o catálogo por origem geográfica.

### `pedidos`
Número inteiro com a quantidade de pedidos já recebidos pelo produto (varia de 8 a 42 no catálogo). Indica a popularidade do produto.

### `cestas`
Lista de compras, em que cada compra é uma lista com os `id` dos produtos comprados juntos (por exemplo, `["p01", "p02"]`). Cada cesta tem de 2 a 3 itens e serve para descobrir quais produtos costumam ser comprados em conjunto.

### `estoque`
Quantidade de unidades disponíveis do produto. Quando é 0, o produto não é recomendado.

### `artesao_id`
Identificador do artesão que produz o produto (ex.: `a02`). Permite ligar vários produtos ao mesmo artesão.

### `nome_artesao`
Nome do artesão que aparece na recomendação. São nomes inventados, não correspondem a pessoas reais.