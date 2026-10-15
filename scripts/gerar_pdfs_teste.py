"""Gera PDFs jurídicos FICTÍCIOS para testar o pipeline.

1. peticao_inicial.pdf     - texto nativo, 2 páginas, acentuação
2. acordao_tabela.pdf      - texto nativo com tabela
3. contrato_escaneado.pdf  - só imagem (simula digitalização: rotação + ruído) -> exige OCR
"""

import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("Serif", FONT_DIR / "DejaVuSerif.ttf"))
pdfmetrics.registerFont(TTFont("Serif-B", FONT_DIR / "DejaVuSerif-Bold.ttf"))

corpo = ParagraphStyle("corpo", fontName="Serif", fontSize=11, leading=16, alignment=TA_JUSTIFY, firstLineIndent=1.5 * cm)
titulo = ParagraphStyle("titulo", fontName="Serif-B", fontSize=13, leading=18, alignment=TA_CENTER, spaceAfter=12)
cabec = ParagraphStyle("cabec", fontName="Serif-B", fontSize=11, leading=16, spaceBefore=10, spaceAfter=6)


def doc(path: Path, story):
    SimpleDocTemplate(str(path), pagesize=A4, leftMargin=3 * cm, rightMargin=2 * cm, topMargin=2.5 * cm,
                      bottomMargin=2 * cm, title=path.stem, author="Gerador de testes juris-pdf").build(story)


def peticao(path: Path):
    P = lambda t, s=corpo: Paragraph(t, s)  # noqa: E731
    story = [
        P("EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DE DIREITO DA 3ª VARA CÍVEL DA COMARCA DE VILA FICTÍCIA", titulo),
        Spacer(1, 18),
        P("<b>MARIA APARECIDA DOS EXEMPLOS</b>, brasileira, solteira, professora, inscrita no CPF sob o nº 000.000.000-00, "
          "residente na Rua das Hipóteses, nº 42, vem, por seu advogado, propor a presente"),
        P("AÇÃO DE INDENIZAÇÃO POR DANOS MATERIAIS E MORAIS", titulo),
        P("em face de <b>EMPRESA DEMONSTRATIVA LTDA.</b>, pessoa jurídica de direito privado, CNPJ 00.000.000/0001-00, "
          "pelos fatos e fundamentos a seguir expostos."),
        P("I – DOS FATOS", cabec),
        P("Em 15 de março de 2026, a Autora adquiriu junto à Ré um aparelho de ar-condicionado, no valor de R$ 3.450,00 "
          "(três mil, quatrocentos e cinquenta reais), cuja entrega estava prevista para 22 de março de 2026. "
          "Decorridos mais de noventa dias, o produto não foi entregue, tampouco houve restituição do valor pago."),
        P("A Autora realizou diversas reclamações administrativas (protocolos nº 2026-0001 e 2026-0002), "
          "sem qualquer solução por parte da Ré, o que lhe causou transtornos que ultrapassam o mero aborrecimento."),
        PageBreak(),
        P("II – DO DIREITO", cabec),
        P("A relação jurídica estabelecida entre as partes é de consumo, aplicando-se o Código de Defesa do Consumidor "
          "(Lei nº 8.078/1990). Nos termos do art. 35, inciso III, do referido diploma, o consumidor pode rescindir o "
          "contrato, com direito à restituição de quantia eventualmente antecipada, monetariamente atualizada, "
          "e a perdas e danos."),
        P("Ademais, o art. 6º, inciso VI, assegura a efetiva prevenção e reparação de danos patrimoniais e morais."),
        P("III – DOS PEDIDOS", cabec),
        P("Ante o exposto, requer: (a) a citação da Ré; (b) a condenação da Ré à restituição de R$ 3.450,00, "
          "corrigidos monetariamente; (c) a condenação ao pagamento de indenização por danos morais no valor de "
          "R$ 10.000,00; (d) a inversão do ônus da prova, nos termos do art. 6º, VIII, do CDC."),
        P("Dá-se à causa o valor de R$ 13.450,00."),
        Spacer(1, 24),
        P("Vila Fictícia, 1º de julho de 2026.", ParagraphStyle("c", parent=corpo, alignment=TA_CENTER, firstLineIndent=0)),
        P("ADVOGADO DE TESTE – OAB/XX 000.000", ParagraphStyle("c", parent=corpo, alignment=TA_CENTER, firstLineIndent=0)),
    ]
    doc(path, story)


def acordao(path: Path):
    P = lambda t, s=corpo: Paragraph(t, s)  # noqa: E731
    dados = [
        ["Parcela", "Valor (R$)", "Índice", "Termo inicial"],
        ["Restituição do preço", "3.450,00", "IPCA-E", "15/03/2026"],
        ["Danos morais", "8.000,00", "Selic", "Data do arbitramento"],
        ["Honorários (15%)", "1.717,50", "—", "Trânsito em julgado"],
        ["Total", "13.167,50", "", ""],
    ]
    t = Table(dados, colWidths=[5 * cm, 3 * cm, 2.5 * cm, 4.5 * cm])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Serif", 10),
        ("FONT", (0, 0), (-1, 0), "Serif-B", 10),
        ("FONT", (0, -1), (-1, -1), "Serif-B", 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
    ]))
    story = [
        P("TRIBUNAL DE JUSTIÇA DO ESTADO FICTÍCIO", titulo),
        P("Apelação Cível nº 0000000-00.2026.8.99.0001 – 5ª Câmara de Direito Privado", ParagraphStyle("c", parent=corpo, alignment=TA_CENTER, firstLineIndent=0)),
        Spacer(1, 12),
        P("EMENTA", cabec),
        P("APELAÇÃO CÍVEL. DIREITO DO CONSUMIDOR. COMPRA E VENDA. ATRASO NA ENTREGA DE PRODUTO. "
          "DANO MORAL CONFIGURADO. REDUÇÃO DO QUANTUM INDENIZATÓRIO. RECURSO PARCIALMENTE PROVIDO. "
          "1. A ausência de entrega do produto adquirido, aliada à falta de solução administrativa, configura "
          "falha na prestação do serviço. 2. Valor da indenização reduzido para R$ 8.000,00, em atenção aos "
          "princípios da razoabilidade e da proporcionalidade."),
        P("ACÓRDÃO", cabec),
        P("Vistos, relatados e discutidos estes autos, acordam os Desembargadores da 5ª Câmara de Direito Privado, "
          "por unanimidade, em dar parcial provimento ao recurso, nos termos do voto do Relator. "
          "Os valores da condenação ficam assim discriminados:"),
        Spacer(1, 8), t, Spacer(1, 12),
        P("Relator: Des. EXEMPLO DE SOUZA. Julgado em 10 de setembro de 2026."),
    ]
    doc(path, story)


def contrato_escaneado(path: Path):
    """Desenha o texto numa imagem (300 dpi), gira e adiciona ruído — PDF sem camada de texto."""
    random.seed(7)
    W, H = 2480, 3508  # A4 @ 300 dpi
    img = Image.new("L", (W, H), 250)
    d = ImageDraw.Draw(img)
    f_t = ImageFont.truetype(str(FONT_DIR / "DejaVuSerif-Bold.ttf"), 54)
    f = ImageFont.truetype(str(FONT_DIR / "DejaVuSerif.ttf"), 42)
    linhas = [
        ("CONTRATO PARTICULAR DE LOCAÇÃO RESIDENCIAL", f_t),
        ("", f),
        ("LOCADOR: João Fictício da Silva, CPF 000.000.000-00.", f),
        ("LOCATÁRIA: Ana Exemplar Pereira, CPF 111.111.111-11.", f),
        ("", f),
        ("CLÁUSULA PRIMEIRA – DO OBJETO", f_t),
        ("O LOCADOR dá em locação à LOCATÁRIA o imóvel situado na", f),
        ("Avenida dos Testes, nº 100, apto. 21, Vila Fictícia.", f),
        ("", f),
        ("CLÁUSULA SEGUNDA – DO PRAZO", f_t),
        ("A locação vigorará pelo prazo de 30 (trinta) meses, com", f),
        ("início em 1º de agosto de 2026 e término em 31 de janeiro de 2029.", f),
        ("", f),
        ("CLÁUSULA TERCEIRA – DO ALUGUEL", f_t),
        ("O aluguel mensal é de R$ 2.300,00 (dois mil e trezentos reais),", f),
        ("reajustado anualmente pelo IGP-M, com vencimento todo dia 5.", f),
        ("", f),
        ("CLÁUSULA QUARTA – DA MULTA", f_t),
        ("A rescisão antecipada sujeitará a parte infratora à multa", f),
        ("equivalente a 3 (três) aluguéis, proporcional ao tempo restante,", f),
        ("nos termos do art. 4º da Lei nº 8.245/1991.", f),
        ("", f),
        ("Vila Fictícia, 25 de julho de 2026.", f),
    ]
    y = 260
    for txt, font in linhas:
        d.text((250, y), txt, fill=20, font=font)
        y += 85
    d.line((250, y + 150, 1050, y + 150), fill=30, width=3)
    d.text((250, y + 165), "LOCADOR", fill=30, font=f)
    d.line((1350, y + 150, 2150, y + 150), fill=30, width=3)
    d.text((1350, y + 165), "LOCATÁRIA", fill=30, font=f)

    img = img.rotate(1.2, fillcolor=250, resample=Image.BICUBIC)  # digitalização torta
    px = img.load()
    for _ in range(40000):  # sujeira de scanner
        px[random.randrange(W), random.randrange(H)] = random.randint(80, 200)
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    img.save(path, "PDF", resolution=300)


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "dados/entrada")
    out.mkdir(parents=True, exist_ok=True)
    peticao(out / "peticao_inicial.pdf")
    acordao(out / "acordao_tabela.pdf")
    contrato_escaneado(out / "contrato_escaneado.pdf")
    for p in sorted(out.glob("*.pdf")):
        print(f"{p}  ({p.stat().st_size / 1024:.0f} KB)")
