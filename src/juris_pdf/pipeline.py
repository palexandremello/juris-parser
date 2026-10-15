"""Pipeline: PDF -> (OCR se necessário) -> texto, markdown, docx + manifesto."""

from __future__ import annotations

import hashlib
import io
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

from .client import StirlingClient

MIN_CHARS_PER_PAGE = 50  # abaixo disso, consideramos a página "sem texto" (escaneada)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def text_layer_stats(pdf_bytes: bytes) -> tuple[int, int]:
    """(nº de páginas, nº de páginas com camada de texto útil)."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    with_text = sum(1 for p in reader.pages if len((p.extract_text() or "").strip()) >= MIN_CHARS_PER_PAGE)
    return len(reader.pages), with_text


@dataclass
class Resultado:
    arquivo: str
    sha256_original: str
    paginas: int
    paginas_com_texto: int
    ocr_aplicado: bool
    saidas: dict[str, str] = field(default_factory=dict)  # nome -> sha256
    tempos_s: dict[str, float] = field(default_factory=dict)
    erros: list[str] = field(default_factory=list)


def processar_pdf(client: StirlingClient, pdf_path: Path, out_root: Path, formatos=("txt", "md", "docx")) -> Resultado:
    original = pdf_path.read_bytes()
    paginas, com_texto = text_layer_stats(original)
    res = Resultado(pdf_path.name, sha256(original), paginas, com_texto, ocr_aplicado=False)

    out = out_root / pdf_path.stem
    out.mkdir(parents=True, exist_ok=True)

    def salvar(nome: str, dados: bytes):
        (out / nome).write_bytes(dados)
        res.saidas[nome] = sha256(dados)

    trabalho = original
    if com_texto < paginas:  # alguma página sem texto -> OCR
        t = time.perf_counter()
        try:
            trabalho = client.ocr(original)
            res.ocr_aplicado = True
            salvar(f"{pdf_path.stem}.ocr.pdf", trabalho)
        except Exception as e:  # noqa: BLE001
            res.erros.append(f"ocr: {e}")
        res.tempos_s["ocr"] = round(time.perf_counter() - t, 2)

    conversores = {
        "txt": lambda b: client.to_text(b).encode("utf-8"),
        "md": lambda b: client.to_markdown(b).encode("utf-8"),
        "docx": client.to_docx,
    }
    for fmt in formatos:
        t = time.perf_counter()
        try:
            salvar(f"{pdf_path.stem}.{fmt}", conversores[fmt](trabalho))
        except Exception as e:  # noqa: BLE001
            res.erros.append(f"{fmt}: {e}")
        res.tempos_s[fmt] = round(time.perf_counter() - t, 2)
    return res


def processar_pasta(entrada: Path, saida: Path, client: StirlingClient | None = None) -> dict:
    own = client is None
    client = client or StirlingClient()
    try:
        status = client.status()
        resultados = [processar_pdf(client, p, saida) for p in sorted(entrada.glob("*.pdf"))]
    finally:
        if own:
            client.close()
    manifesto = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "backend": {"ferramenta": "Stirling-PDF", **status},
        "documentos": [asdict(r) for r in resultados],
    }
    saida.mkdir(parents=True, exist_ok=True)
    (saida / "manifesto.json").write_text(json.dumps(manifesto, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifesto
