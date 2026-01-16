"""
PDF Service - Generate receipt PDFs
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import os


class ReceiptPDFService:
    """Service for generating receipt PDFs"""

    def __init__(self):
        """Initialize PDF service and register fonts"""
        self._register_fonts()

    def _register_fonts(self):
        """Register Chinese fonts"""
        # Try to find system Chinese fonts
        font_paths = [
            'C:/Windows/Fonts/msjh.ttc',      # Microsoft JhengHei
            'C:/Windows/Fonts/mingliu.ttc',   # MingLiU
            'C:/Windows/Fonts/simsun.ttc',    # SimSun
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',  # Linux
        ]

        font_registered = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path, subfontIndex=0))
                    font_registered = True
                    break
                except Exception:
                    continue

        if not font_registered:
            # Fallback to default
            self.chinese_font = 'Helvetica'
        else:
            self.chinese_font = 'ChineseFont'

    def generate(self, receipt):
        """
        Generate PDF for a receipt

        Args:
            receipt: Receipt object

        Returns:
            BytesIO object containing PDF data
        """
        buffer = BytesIO()

        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # Build content
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontName=self.chinese_font,
            fontSize=18,
            alignment=1,  # Center
            spaceAfter=6
        )
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=14,
            alignment=1,
            spaceAfter=12
        )
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=11
        )
        right_style = ParagraphStyle(
            'Right',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            alignment=2  # Right
        )

        # Title
        elements.append(Paragraph('\u81fa\u5317\u5e02\u7acb\u5927\u5b78', title_style))
        elements.append(Paragraph('\u6e38\u6cf3\u6c60\u6536\u8cbb\u6536\u64da', subtitle_style))

        # Date and receipt number
        created_at = receipt.created_at.strftime('%Y/%m/%d %H:%M:%S') if receipt.created_at else ''
        elements.append(Paragraph(f'{created_at}', right_style))
        elements.append(Paragraph(f'\u6536\u64da\u7de8\u865f: {receipt.receipt_no}', right_style))
        elements.append(Spacer(1, 12))

        # Receipt details table
        table_data = [
            ['\u6536\u8cbb\u9805\u76ee', '\u91d1\u984d', '\u5099\u8a3b'],
            [receipt.item_name, f'{receipt.amount:,.0f}', receipt.remark or ''],
            ['', '', ''],
            ['', '', ''],
            ['', '', ''],
        ]

        table = Table(table_data, colWidths=[10*cm, 3*cm, 4*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        # Total
        total_style = ParagraphStyle(
            'Total',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=12,
            alignment=0
        )
        elements.append(Paragraph(f'\u5408\u8a08\uff1a{receipt.amount:,.0f} \u5143', total_style))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(f'\u65b0\u53f0\u5e63\uff1a{receipt.amount_chinese}', total_style))
        elements.append(Spacer(1, 30))

        # Operator signature
        sig_data = [
            [f'\u7d93\u8fa6\u54e1\uff1a{receipt.operator_name}', '', '[\u6e38\u6cf3\u6c60\u6536\u8cbb\u5c08\u7528\u7ae0]']
        ]
        sig_table = Table(sig_data, colWidths=[6*cm, 6*cm, 5*cm])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ]))
        elements.append(sig_table)
        elements.append(Spacer(1, 20))

        # Footer note
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontName=self.chinese_font,
            fontSize=9,
            alignment=1,
            textColor=colors.grey
        )
        elements.append(Paragraph('\u672c\u6536\u64da\u70ba\u6e38\u6cf3\u6c60\u73fe\u91d1\u6536\u8cbb\u8b49\u660e\uff0c\u8acb\u59a5\u5584\u4fdd\u7ba1', footer_style))

        # Build PDF
        doc.build(elements)

        buffer.seek(0)
        return buffer

    def generate_report(self, title, data, columns, summary=None):
        """
        Generate a report PDF

        Args:
            title: Report title
            data: List of row data
            columns: List of column headers
            summary: Optional summary dict

        Returns:
            BytesIO object containing PDF data
        """
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontName=self.chinese_font,
            fontSize=16,
            alignment=1,
            spaceAfter=20
        )

        # Title
        elements.append(Paragraph(title, title_style))

        # Data table
        table_data = [columns] + data

        # Calculate column widths based on number of columns
        col_count = len(columns)
        available_width = 17 * cm
        col_width = available_width / col_count

        table = Table(table_data, colWidths=[col_width] * col_count)
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)

        # Summary
        if summary:
            elements.append(Spacer(1, 20))
            summary_style = ParagraphStyle(
                'Summary',
                parent=styles['Normal'],
                fontName=self.chinese_font,
                fontSize=11
            )
            for key, value in summary.items():
                elements.append(Paragraph(f'{key}: {value}', summary_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer
