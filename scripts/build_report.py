#!/usr/bin/env python3
"""Render the editable Markdown report with the bundled ReportLab runtime."""
from pathlib import Path
import re
from html import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4

R=Path(__file__).resolve().parents[1]
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyCustom',fontName='Helvetica',fontSize=10,leading=14,spaceAfter=9,textColor=colors.HexColor('#203247')))
styles.add(ParagraphStyle(name='TitleCustom',fontName='Helvetica-Bold',fontSize=25,leading=30,spaceAfter=20,textColor=colors.HexColor('#102b46')))
styles.add(ParagraphStyle(name='HeadingCustom',fontName='Helvetica-Bold',fontSize=13,leading=17,spaceBefore=10,spaceAfter=8,textColor=colors.HexColor('#087f8c')))
styles.add(ParagraphStyle(name='TableCustom',fontName='Helvetica',fontSize=8.2,leading=11))
styles.add(ParagraphStyle(name='CodeCustom',fontName='Courier',fontSize=8.5,leading=12,backColor=colors.HexColor('#edf2f6'),borderPadding=8,spaceBefore=6,spaceAfter=12))

def fmt(s):
    s=escape(s)
    s=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',s)
    return s

def table(rows):
    width=A4[0]-96
    cols=len(rows[0])
    widths=([width*.24]+[width*.76] if cols==2 else
            [width*.21,width*.39,width*.40] if cols==3 else [width/cols]*cols)
    if cols==7:
        widths=[width*x for x in (.18,.11,.10,.10,.12,.19,.20)]
    cells=[[Paragraph(fmt(cell.strip()),styles['TableCustom']) for cell in row] for row in rows]
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dcecf1')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f3f6f8')]),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),
        ('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),
        ('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#087f8c'))]))
    return t

story=[]
text=(R/'docs/REPORT.md').read_text()
for section in text.split('<!-- pagebreak -->'):
    if story: story.append(PageBreak())
    lines=section.strip().splitlines(); i=0
    while i<len(lines):
        line=lines[i]
        if not line.strip(): i+=1; continue
        if line.startswith('```'):
            i+=1; code=[]
            while i<len(lines) and not lines[i].startswith('```'):
                code.append(lines[i]); i+=1
            story.append(Preformatted('\n'.join(code),styles['CodeCustom']))
            i+=1; continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                if not re.match(r'^\|[\s:|\-]+\|$',lines[i]):
                    rows.append(lines[i].strip('|').split('|'))
                i+=1
            story += [table(rows),Spacer(1,10)]; continue
        if line.startswith('# '):
            story.append(Paragraph(fmt(line[2:]),styles['TitleCustom'])); i+=1; continue
        if line.startswith('##'):
            story.append(Paragraph(fmt(line.lstrip('#').strip()),styles['HeadingCustom'])); i+=1; continue
        paragraph=[line]; i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','```','- ')):
            paragraph.append(lines[i]); i+=1
        story.append(Paragraph(fmt(' '.join(paragraph)),styles['BodyCustom']))

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor('#c4d5df'))
    canvas.line(48,40,A4[0]-48,40)
    canvas.setFont('Helvetica',8)
    canvas.setFillColor(colors.HexColor('#586d7e'))
    canvas.drawString(48,27,'Modern Computer Architecture / Direct-Mapped Cache Controller')
    canvas.drawRightString(A4[0]-48,27,str(doc.page))
    canvas.restoreState()

out=R/'output/pdf/Cache_Controller_Report.pdf'
out.parent.mkdir(parents=True,exist_ok=True)
SimpleDocTemplate(str(out),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=45,bottomMargin=55,
                  title='Direct-Mapped Cache Controller',author='Modern Computer Architecture Project').build(story,onFirstPage=footer,onLaterPages=footer)
print(out)
