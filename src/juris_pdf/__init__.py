"""juris-pdf: conversão de documentos jurídicos usando Stirling-PDF como backend."""

import argparse
from pathlib import Path

from .client import StirlingClient
from .pipeline import processar_pasta


def main() -> None:
    ap = argparse.ArgumentParser(prog="juris-pdf")
    ap.add_argument("entrada", type=Path, help="pasta com PDFs")
    ap.add_argument("-o", "--saida", type=Path, default=Path("saida"))
    ap.add_argument("--url", default=None, help="URL do Stirling (padrão: $STIRLING_URL ou localhost:8080)")
    a = ap.parse_args()

    client = StirlingClient(a.url) if a.url else StirlingClient()
    with client:
        m = processar_pasta(a.entrada, a.saida, client)
    for d in m["documentos"]:
        ocr = "OCR" if d["ocr_aplicado"] else "texto nativo"
        status = "ERROS: " + "; ".join(d["erros"]) if d["erros"] else "ok"
        print(f"{d['arquivo']:<40} {d['paginas']:>2} pág  {ocr:<13} {d['tempos_s']}  {status}")
    print(f"\nManifesto: {a.saida / 'manifesto.json'}")
