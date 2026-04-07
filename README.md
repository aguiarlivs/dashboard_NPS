# Dashboard NPS

Apresentação dos resultados do NPS em um dashboard estático gerado a partir de `dados7abr.csv`.

## Estrutura

- `main.py`: gera o `index.html`
- `styles.css`: estilos do dashboard
- `dashboard.js`: filtros, atualização dinâmica e exportação/impressão
- `dados7abr.csv`: base de dados
- `index.html`: artefato gerado para apresentação

## Como atualizar o dashboard

1. Instale as dependências:

```bash
pip install -r requirements.txt
```

2. Gere novamente o HTML:

```bash
python3 main.py
```

3. Abra o arquivo `index.html` no navegador.

## Observações

- O dashboard usa exclusivamente o CSV local.
- O botão `Exportar / Imprimir` abre uma versão otimizada para PDF/print.
