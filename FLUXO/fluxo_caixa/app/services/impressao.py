"""Serviço de impressão de relatórios

Gera PDF com layout corporativo usando reportlab e permite impressão direta no Windows.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from datetime import datetime
from pathlib import Path
import os
import tempfile


def gerar_pdf_relatorio(nome_sistema: str, periodo: str, lancamentos: list, totais: dict, caminho_saida: Path = None) -> Path:
    """Gera PDF do relatório e retorna o caminho do arquivo gerado.

    Args:
        nome_sistema: nome do sistema (cabeçalho)
        periodo: texto do período (ex: 2025-01-01 a 2025-12-31)
        lancamentos: lista de dicts com chaves: data, tipo, categoria, descricao, valor
        totais: dict com chaves 'entradas','saidas','saldo'
        caminho_saida: Path opcional para salvar; se None usa tempdir
    """
    if caminho_saida is None:
        caminho_saida = Path(tempfile.gettempdir()) / f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    doc = SimpleDocTemplate(str(caminho_saida), pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    elements = []

    # Cabeçalho
    titulo_style = ParagraphStyle('Titulo', parent=styles['Heading1'], alignment=1, fontSize=14, leading=16)
    meta_style = ParagraphStyle('Meta', parent=styles['Normal'], alignment=1, fontSize=9)

    elements.append(Paragraph(nome_sistema, titulo_style))
    elements.append(Paragraph(f"Período: {periodo}", meta_style))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", meta_style))
    elements.append(Spacer(1, 8))

    # Totais consolidados
    tot_items = [
        ["Entradas", f"R$ {totais.get('entradas', 0):,.2f}"],
        ["Saídas", f"R$ {totais.get('saidas', 0):,.2f}"],
        ["Saldo", f"R$ {totais.get('saldo', 0):,.2f}"]
    ]
    t = Table([['', ''], ['', '']], colWidths=[100*mm, 60*mm])
    t = Table(tot_items, colWidths=[100*mm, 60*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 10))

    # Tabela de lançamentos
    data = [['Data', 'Tipo', 'Categoria', 'Descrição', 'Valor']]
    for l in lancamentos:
        data.append([
            l.get('data', ''),
            l.get('tipo', '').title(),
            l.get('categoria', ''),
            (l.get('descricao') or '')[:80],
            f"R$ {l.get('valor', 0):,.2f}"
        ])

    table = Table(data, colWidths=[22*mm, 24*mm, 40*mm, 70*mm, 30*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#bdc3c7')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f7f9fa')])
    ]))

    elements.append(table)

    doc.build(elements)
    return caminho_saida


def imprimir_pdf_windows(caminho_pdf: Path) -> None:
    """Imprime PDF no Windows usando os.startfile('print')."""
    if os.name == 'nt':
        try:
            os.startfile(str(caminho_pdf), 'print')
        except Exception:
            # fallback: abrir para visualização
            os.startfile(str(caminho_pdf))
    else:
        # Não suportado diretamente: apenas abre
        if hasattr(os, 'startfile'):
            os.startfile(str(caminho_pdf))
        else:
            # Tentar abrir com xdg-open / open
            try:
                import subprocess
                if os.name == 'posix':
                    subprocess.run(['xdg-open', str(caminho_pdf)])
            except Exception:
                pass

