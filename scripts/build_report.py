#!/usr/bin/env python3
"""Export docs/REPORT.md to PDF without changing the maintained source.

Requires ReportLab. Supports the report's headings, tables, inline emphasis,
code, lists, horizontal rules and explicit HTML page-break comments.
"""
import argparse
from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable, PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer,
    Table, TableStyle, BaseDocTemplate, Frame, PageTemplate, FrameBreak, NextPageTemplate, Image, KeepTogether,
)

ROOT = Path(__file__).resolve().parents[1]
WIDTH = 252  # IEEE conference column: 3.5 inches, with a 0.25-inch gutter
INK = colors.black
TEAL = colors.black
STYLES = getSampleStyleSheet()
STYLES.add(ParagraphStyle(name='ReportBody', fontName='Times-Roman', fontSize=10,
    leading=11.6, spaceAfter=6, alignment=4, textColor=INK))
STYLES.add(ParagraphStyle(name='ReportTitle', fontName='Times-Bold', fontSize=10,
    leading=12, spaceBefore=9, spaceAfter=5, alignment=1, textColor=colors.black, keepWithNext=True))
STYLES.add(ParagraphStyle(name='ReportHeading', fontName='Times-Bold', fontSize=10,
    leading=12, spaceBefore=7, spaceAfter=4, textColor=TEAL, keepWithNext=True))
STYLES.add(ParagraphStyle(name='ReportCell', fontName='Times-Roman', fontSize=7.5,
    leading=9, textColor=INK))
STYLES.add(ParagraphStyle(name='ReportCode', fontName='Courier', fontSize=8.2,
    leading=12, backColor=colors.HexColor('#edf2f6'), borderPadding=8,
    spaceBefore=6, spaceAfter=12))
STYLES.add(ParagraphStyle(name='ReportBullet', parent=STYLES['ReportBody'],
    leftIndent=12, bulletIndent=0, spaceAfter=5))


def normalize(text):
    return text.translate(str.maketrans({
        '\u2014': ' - ', '\u2013': '-', '\u2011': '-', '\u2010': '-',
        '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
        '\u00d7': 'x', '\u00a0': ' ',
    }))


def inline(text):
    """Escape input before adding the small supported set of PDF markup."""
    code = []
    def save_code(match):
        code.append('<font name="Courier">' + escape(normalize(match[1])) + '</font>')
        return f'ZZCODETOKEN{len(code)-1}ZZ'
    text = re.sub(r'`([^`]+)`', save_code, text)
    text = escape(normalize(text))
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',
                  r'<link href="\2" color="#087f8c">\1</link>', text)
    for i, value in enumerate(code):
        text = text.replace(f'ZZCODETOKEN{i}ZZ', value)
    return text


def make_table(rows):
    count = len(rows[0])
    if any(len(row) != count for row in rows):
        raise ValueError('Table rows have different column counts')
    if count == 2:
        shares = (.70, .30) if 'Project component' in rows[0][0] else (.29, .71)
    elif count == 3:
        shares = (.24, .38, .38)
    elif count == 7:
        shares = (.18, .11, .10, .10, .12, .19, .20)
    else:
        shares = (1/count,) * count
    cells = [[Paragraph(inline(cell.strip()), STYLES['ReportCell']) for cell in row] for row in rows]
    table = Table(cells, colWidths=[WIDTH*s for s in shares], repeatRows=1, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#eeeeee')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.white]),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 3), ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,0), .5, TEAL),
    ]))
    return table


def parse(markdown):
    story = []
    references = False
    for section in markdown.split('<!-- pagebreak -->'):
        if story:
            story.append(PageBreak())
        lines = section.strip().splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            if line == '<!-- columnbreak -->':
                story.append(FrameBreak())
                i += 1
                continue
            if re.fullmatch(r'[-*_]{3,}', line):
                story.extend([HRFlowable(width=WIDTH, thickness=.5,
                    color=colors.HexColor('#c4d5df')), Spacer(1, 10)])
                i += 1
                continue
            figure = re.fullmatch(r'!\[(.*?)\]\((.*?)\)', line)
            if figure:
                path = ROOT/'docs'/figure[2]
                from PIL import Image as PILImage
                with PILImage.open(path) as picture:
                    w, h = picture.size
                scale = min(WIDTH/w, 285/h)
                caption = Paragraph(inline(figure[1]), ParagraphStyle(
                    name='FigureCaption', fontName='Times-Roman', fontSize=8,
                    leading=9.5, alignment=1, spaceAfter=8))
                story.append(KeepTogether([Image(str(path), width=w*scale, height=h*scale), caption]))
                i += 1
                continue
            if line.startswith('```'):
                i += 1
                code = []
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code.append(normalize(lines[i]))
                    i += 1
                if i == len(lines):
                    raise ValueError('Unclosed fenced code block')
                story.append(Preformatted('\n'.join(code), STYLES['ReportCode']))
                i += 1
                continue
            if line.startswith('|'):
                rows = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    value = lines[i].strip()
                    if not re.fullmatch(r'\|[\s:|\-]+\|', value):
                        rows.append(value.strip('|').split('|'))
                    i += 1
                story.extend([make_table(rows), Spacer(1, 10)])
                continue
            heading = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading:
                major = len(heading[1]) == 1 or bool(re.match(r'^[IVX]+\.\s', heading[2])) or heading[2] == 'References'
                style = 'ReportTitle' if major else 'ReportHeading'
                references = heading[2] == 'References'
                label = heading[2].upper() if major else heading[2]
                story.append(Paragraph(inline(label), STYLES[style]))
                i += 1
                continue
            bullet = re.match(r'^[-*]\s+(.+)$', line)
            numbered = re.match(r'^(\d{1,2})\.\s+(.+)$', line)
            if bullet or numbered:
                value = bullet[1] if bullet else numbered[2]
                marker = '-' if bullet else numbered[1] + '.'
                story.append(Paragraph(inline(value), STYLES['ReportBullet'], bulletText=marker))
                i += 1
                continue
            paragraph = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(
                    r'^(#|!\[|\||```|[-*]\s|\d{1,2}\.\s|---+$)', lines[i].strip()):
                paragraph.append(lines[i].strip())
                i += 1
            value=' '.join(paragraph)
            if value.startswith('**Abstract -**'):
                style=ParagraphStyle(name='Abstract',parent=STYLES['ReportBody'],fontName='Times-Bold',fontSize=9,leading=10.5)
            elif references:
                style=ParagraphStyle(name='Reference',parent=STYLES['ReportBody'],fontSize=8,leading=9.5,alignment=0)
            else:
                style=STYLES['ReportBody']
            item=Paragraph(inline(value),style)
            story.append(KeepTogether([item]) if references else item)
    return story


def main():
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'output/pdf/Cache_Controller_Report.pdf')
    args = parser.parse_args()
    source = ROOT/'docs/REPORT.md'
    output = args.output.resolve()
    if output == source.resolve() or output.suffix.lower() != '.pdf':
        parser.error('Output must be a .pdf file distinct from the Markdown source')
    output.parent.mkdir(parents=True, exist_ok=True)
    content = source.read_text()
    team_file=ROOT/'docs/team.json'
    if team_file.exists():
        members=json.loads(team_file.read_text())['members']
    else:
        members=[{'name':name.strip(),'roll':roll} for name,roll in
                 re.findall(r'^\| ([^|]+) \| (\d{10}) \|',content,re.M)]
        if not members:
            raise ValueError('No members found in the report contribution table')
    title = content.splitlines()[0].lstrip('# ')
    body = re.sub(r'^## Abstract\s*\n\s*', '**Abstract -** ', content[content.index('## Abstract'):], count=1)
    title_style = ParagraphStyle(name='PaperTitle',fontName='Times-Roman',fontSize=24,
        leading=27,alignment=1,spaceAfter=10)
    author_style = ParagraphStyle(name='PaperAuthors',fontName='Times-Roman',fontSize=11,
        leading=14,alignment=1,spaceAfter=4)
    course_style = ParagraphStyle(name='PaperCourse',fontName='Times-Roman',fontSize=10,
        leading=12,alignment=1)
    # Letter page: 0.625-inch side margins, 0.75-inch top, 1-inch bottom.
    # Title spans both columns. Subsequent content uses 3.5-inch columns.
    left, bottom, top, title_height, gap = 45, 72, 738, 115, 18
    first_top = top-title_height
    first_frames = [
        Frame(left,first_top,522,title_height,id='title',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0),
        Frame(left,bottom,WIDTH,first_top-bottom,id='first-left',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0),
        Frame(left+WIDTH+gap,bottom,WIDTH,first_top-bottom,id='first-right',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0),
    ]
    body_frames = [Frame(x,bottom,WIDTH,top-bottom,id=name,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
                   for x,name in [(left,'left'),(left+WIDTH+gap,'right')]]
    doc=BaseDocTemplate(str(output),pagesize=letter,title=title,
        author=', '.join(m['name'] for m in members),
        subject='IEEE conference-style two-column project report')
    doc.addPageTemplates([PageTemplate(id='first',frames=first_frames),
                          PageTemplate(id='body',frames=body_frames)])
    story=[Paragraph(inline(title),title_style),
           Paragraph(' &nbsp; &nbsp; '.join(inline(m['name']) for m in members),author_style),
           Paragraph(' &nbsp; &nbsp; '.join(inline(m['roll']) for m in members),course_style),
           Paragraph('B.Tech (CS &amp; AI) - Modern Computer Architecture',course_style),
           NextPageTemplate('body'),FrameBreak()]
    story += parse(body)
    doc.build(story)
    print(output)


if __name__ == '__main__':
    main()
