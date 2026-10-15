# juris-pdf

Protótipo de pesquisa: conversão de documentos jurídicos (petições, acórdãos, contratos, inclusive escaneados)
para texto, Markdown e DOCX, usando o **Stirling-PDF** como backend via API REST.

## Fluxo

```
PDF ──► tem camada de texto? ──não──► OCR (Stirling /misc/ocr-pdf, Tesseract "por")
             │sim                         │
             └──────────────┬─────────────┘
                            ▼
              /convert/pdf/text      → .txt
              /convert/pdf/markdown  → .md
              /convert/pdf/word      → .docx
                            ▼
              manifesto.json  (SHA-256 do original e de cada saída, tempos, versão do backend)
```

Uma página é considerada "sem texto" quando o pypdf extrai menos de 50 caracteres dela.

## Uso

```bash
docker compose up -d                       # sobe o Stirling em localhost:8080
uv sync
uv run python scripts/gerar_pdfs_teste.py  # cria 3 PDFs fictícios em dados/entrada
uv run juris-pdf dados/entrada -o dados/saida
uv run pytest -q                           # testes de integração (pulados se o Stirling estiver fora)
```

Variáveis: `STIRLING_URL` (padrão `http://localhost:8080`), `STIRLING_API_KEY` (se ativar login no Stirling).

## Notas de desempenho (medidas no teste, 1 vCPU)

- OCR é o passo caro (~3,7 s/página) e roda só na CPU (Tesseract); GPU não acelera o Stirling.
- DOCX depende do LibreOffice residente (`unoserver`). Sem ele, cada conversão abre um `soffice` frio: ~56 s → 0,5 s com ele.
  A imagem Docker já cuida disso.

## Limitações conhecidas

- Markdown: em tabelas, colunas adjacentes podem ser fundidas (ex.: "Valor (R$) Índice").
- Os PDFs em `dados/entrada` são **fictícios** (nomes, CPFs e processos inventados).
