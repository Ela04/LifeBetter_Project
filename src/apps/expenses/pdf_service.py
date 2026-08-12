# src/apps/expenses/pdf_service.py
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm


class PDFGeneratorService:
    @staticmethod
    def generate_expense_bill_pdf(bill) -> bytes:
        """
        Genera el documento PDF en memoria para la boleta de cobro de un gasto común.
        Retorna el archivo binario (bytes).
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm
        )

        story = []
        styles = getSampleStyleSheet()

        # Estilos Personalizados (Paleta Verde Verde Institucional)
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            textColor=colors.HexColor('#3a8a3a'),
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor('#6c757d'),
            spaceAfter=15
        )

        normal_style = styles['Normal']
        bold_style = ParagraphStyle('BoldText', parent=normal_style, fontName='Helvetica-Bold')

        # 1. Encabezado del Sistema
        story.append(Paragraph("LifeBetter SaaS - Sistema de Gestión", title_style))
        story.append(Paragraph(f"Condominio: {bill.department.condominium.name} | RUT: {bill.department.condominium.rut}", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3a8a3a'), spaceAfter=20))

        # 2. Información del Cobro y Departamento
        resident_name = bill.department.resident.get_full_name() if bill.department.resident else "Sin Residente Asignado"
        resident_email = bill.department.resident.email if bill.department.resident else "N/A"

        info_data = [
            [
                Paragraph("<b>N° Boleta:</b>", normal_style), Paragraph(f"BOL-{bill.id:06d}", bold_style),
                Paragraph("<b>Departamento:</b>", normal_style), Paragraph(f"N° {bill.department.number} (Piso {bill.department.floor})", bold_style)
            ],
            [
                Paragraph("<b>Periodo:</b>", normal_style), Paragraph(bill.common_expense.period.strftime("%Y-%m"), normal_style),
                Paragraph("<b>Alícuota Aplicada:</b>", normal_style), Paragraph(f"{bill.department.share_percentage * 100:.2f}%", normal_style)
            ],
            [
                Paragraph("<b>Titular:</b>", normal_style), Paragraph(resident_name, normal_style),
                Paragraph("<b>Fecha Vencimiento:</b>", normal_style), Paragraph(bill.due_date.strftime("%d/%m/%Y"), normal_style)
            ],
            [
                Paragraph("<b>Estado de Pago:</b>", normal_style), Paragraph(bill.get_status_display().upper(), bold_style),
                Paragraph("<b>Correo Contacto:</b>", normal_style), Paragraph(resident_email, normal_style)
            ]
        ]

        info_table = Table(info_data, colWidths=[3.5 * cm, 5 * cm, 4 * cm, 5 * cm])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 20))

        # 3. Detalle Financiero de la Liquidación
        story.append(Paragraph("<b>Detalle de Liquidación de Gastos Comunes</b>", ParagraphStyle('Sub', parent=styles['Heading2'], fontSize=12, spaceAfter=10)))

        items_data = [
            [Paragraph("<b>Concepto / Descripción</b>", bold_style), Paragraph("<b>Monto Total Edificio</b>", bold_style), Paragraph("<b>Cobro Individual</b>", bold_style)],
            [
                Paragraph(f"{bill.common_expense.title}<br/><font size=8 color='#6c757d'>{bill.common_expense.description or 'Sin observaciones.'}</font>", normal_style),
                Paragraph(f"${bill.common_expense.total_amount:,.0f}".replace(",", "."), normal_style),
                Paragraph(f"${bill.calculated_amount:,.0f}".replace(",", "."), bold_style)
            ]
        ]

        items_table = Table(items_data, colWidths=[9.5 * cm, 4 * cm, 4 * cm])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3a8a3a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 25))

        # 4. Total a Pagar
        total_data = [
            [Paragraph("<b>TOTAL A PAGAR:</b>", ParagraphStyle('Tot', parent=normal_style, fontSize=12, alignment=2)),
             Paragraph(f"${bill.calculated_amount:,.0f}".replace(",", "."), ParagraphStyle('TotVal', parent=bold_style, fontSize=14, textColor=colors.HexColor('#3a8a3a'), alignment=2))]
        ]
        total_table = Table(total_data, colWidths=[13.5 * cm, 4 * cm])
        total_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.HexColor('#3a8a3a')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(total_table)
        story.append(Spacer(1, 30))

        # 5. Pie de página institucional
        story.append(Paragraph("<i>Este documento es un comprobante digital emitido por la plataforma LifeBetter SaaS. Para dudas o consultas contactar a administración.</i>", ParagraphStyle('Foot', parent=normal_style, fontSize=8, textColor=colors.HexColor('#888888'), alignment=1)))

        doc.build(story)
        pdf_value = buffer.getvalue()
        buffer.close()
        return pdf_value