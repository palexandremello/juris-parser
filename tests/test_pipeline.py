"""Testes de integração: exigem um Stirling-PDF rodando (STIRLING_URL, padrão localhost:8080)."""

import importlib.util
import json
from pathlib import Path

import httpx
import pytest

from juris_pdf.client import StirlingClient
from juris_pdf.pipeline import processar_pasta, text_layer_stats

RAIZ = Path(__file__).resolve().parents[1]


def _stirling_no_ar() -> bool:
    try:
        StirlingClient(timeout=3).status()
        return True
    except httpx.HTTPError:
        return False


pytestmark = pytest.mark.skipif(not _stirling_no_ar(), reason="Stirling-PDF não está rodando")


@pytest.fixture(scope="module")
def manifesto(tmp_path_factory):
    spec = importlib.util.spec_from_file_location("gen", RAIZ / "scripts" / "gerar_pdfs_teste.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    entrada = tmp_path_factory.mktemp("entrada")
    gen.peticao(entrada / "peticao_inicial.pdf")
    gen.acordao(entrada / "acordao_tabela.pdf")
    gen.contrato_escaneado(entrada / "contrato_escaneado.pdf")
    saida = tmp_path_factory.mktemp("saida")
    m = processar_pasta(entrada, saida)
    return m, entrada, saida


def _doc(m, nome):
    return next(d for d in m["documentos"] if d["arquivo"] == nome)


def test_sem_erros(manifesto):
    m, *_ = manifesto
    assert len(m["documentos"]) == 3
    assert all(not d["erros"] for d in m["documentos"])


def test_escaneado_nao_tem_texto_e_recebe_ocr(manifesto):
    m, entrada, saida = manifesto
    paginas, com_texto = text_layer_stats((entrada / "contrato_escaneado.pdf").read_bytes())
    assert com_texto == 0
    d = _doc(m, "contrato_escaneado.pdf")
    assert d["ocr_aplicado"]
    txt = (saida / "contrato_escaneado" / "contrato_escaneado.txt").read_text()
    for termo in ["LOCAÇÃO", "R$ 2.300,00", "8.245/1991", "IGP-M"]:
        assert termo in txt, termo


def test_nativo_nao_passa_por_ocr(manifesto):
    m, _, saida = manifesto
    d = _doc(m, "peticao_inicial.pdf")
    assert not d["ocr_aplicado"] and d["paginas"] == 2
    txt = (saida / "peticao_inicial" / "peticao_inicial.txt").read_text()
    assert "Lei nº 8.078/1990" in txt and "R$ 13.450,00" in txt


def test_markdown_tem_tabela(manifesto):
    _, _, saida = manifesto
    md = (saida / "acordao_tabela" / "acordao_tabela.md").read_text()
    assert "|" in md and "13.167,50" in md


def test_manifesto_hashes_batem(manifesto):
    import hashlib
    m, _, saida = manifesto
    disco = json.loads((saida / "manifesto.json").read_text())
    assert disco["backend"]["ferramenta"] == "Stirling-PDF"
    for d in m["documentos"]:
        pasta = saida / Path(d["arquivo"]).stem
        for nome, h in d["saidas"].items():
            assert hashlib.sha256((pasta / nome).read_bytes()).hexdigest() == h
