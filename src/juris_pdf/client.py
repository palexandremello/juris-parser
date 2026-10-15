"""Cliente mínimo para a API REST do Stirling-PDF."""

from __future__ import annotations

import os
from pathlib import Path

import httpx

DEFAULT_URL = os.environ.get("STIRLING_URL", "http://localhost:8080")


class StirlingError(RuntimeError):
    pass


class StirlingClient:
    def __init__(self, base_url: str = DEFAULT_URL, api_key: str | None = None, timeout: float = 300.0):
        headers = {}
        api_key = api_key or os.environ.get("STIRLING_API_KEY")
        if api_key:
            headers["X-API-KEY"] = api_key
        self._http = httpx.Client(base_url=base_url, headers=headers, timeout=timeout)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> StirlingClient:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # --- infra -----------------------------------------------------------
    def status(self) -> dict:
        r = self._http.get("/api/v1/info/status")
        r.raise_for_status()
        return r.json()

    def _post(self, endpoint: str, pdf: Path | bytes, data: dict | None = None) -> bytes:
        content = pdf.read_bytes() if isinstance(pdf, Path) else pdf
        files = {"fileInput": ("input.pdf", content, "application/pdf")}
        r = self._http.post(endpoint, files=files, data=data or {})
        if r.status_code != 200:
            raise StirlingError(f"{endpoint} -> HTTP {r.status_code}: {r.text[:300]}")
        return r.content

    # --- operações ---------------------------------------------------------
    def ocr(self, pdf: Path | bytes, languages: tuple[str, ...] = ("por",), force: bool = False) -> bytes:
        """Retorna um PDF pesquisável (camada de texto via Tesseract/OCRmyPDF)."""
        data = {
            "languages": list(languages),
            "ocrType": "force-ocr" if force else "skip-text",
            "ocrRenderType": "sandwich",
            "deskew": "true",
        }
        return self._post("/api/v1/misc/ocr-pdf", pdf, data)

    def to_text(self, pdf: Path | bytes) -> str:
        return self._post("/api/v1/convert/pdf/text", pdf, {"outputFormat": "txt"}).decode("utf-8", "replace")

    def to_markdown(self, pdf: Path | bytes) -> str:
        return self._post("/api/v1/convert/pdf/markdown", pdf).decode("utf-8", "replace")

    def to_docx(self, pdf: Path | bytes) -> bytes:
        return self._post("/api/v1/convert/pdf/word", pdf, {"outputFormat": "docx"})
