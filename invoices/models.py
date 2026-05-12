from datetime import date
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    company_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return f'{self.user.username} - Approved' if self.approved else f'{self.user.username} - Pending'


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=200)
    event_date = models.DateField(default=date.today)
    shifts_covered = models.PositiveIntegerField(default=1)
    amount_to_be_paid = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='documents/invoices/', null=True, blank=True)

    def __str__(self):
        return f'Invoice {self.id} for {self.user.username} - {self.event_name}'

    def generate_pdf(self):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=72, bottomMargin=36)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('title', parent=styles['Heading1'], fontSize=24, textColor=colors.darkblue, spaceAfter=20, alignment=1)
        header_style = ParagraphStyle('header', parent=styles['Normal'], fontSize=12, textColor=colors.gray, alignment=1)
        normal_style = ParagraphStyle('normal', parent=styles['Normal'], fontSize=11, leading=16)
        bold_style = ParagraphStyle('bold', parent=styles['Normal'], fontSize=11, fontName='Helvetica-Bold', leading=16)

        elements = []

        # Header with logo and company info
        logo_path = settings.BASE_DIR / 'invoices' / 'static' / 'invoices' / 'images' / 'mookhlogo.png'
        try:
            if logo_path.exists():
                logo = Image(str(logo_path), width=160, height=60)
                elements.append(logo)
                elements.append(Spacer(1, 10))
        except Exception:
            pass

        elements.append(Paragraph('Mookh.com', header_style))
        elements.append(Paragraph('Professional Event Services', header_style))
        elements.append(Spacer(1, 20))

        # Invoice title
        elements.append(Paragraph('INVOICE', title_style))
        elements.append(Spacer(1, 20))

        # Invoice details table
        invoice_data = [
            ['Invoice ID:', f'INV-{self.id:04d}'],
            ['Date:', self.created_at.strftime('%B %d, %Y')],
            ['Client:', self.user.get_full_name() or self.user.username],
            ['Email:', self.user.email],
            ['Phone:', self.user.profile.phone or 'Not provided'],
        ]

        invoice_table = Table(invoice_data, colWidths=[2*inch, 4*inch])
        invoice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ]))
        elements.append(invoice_table)
        elements.append(Spacer(1, 20))

        # Event details
        elements.append(Paragraph('<b>Event Details</b>', bold_style))
        event_data = [
            ['Event Name:', self.event_name],
            ['Event Date:', self.event_date.strftime('%B %d, %Y')],
            ['Shifts Covered:', str(self.shifts_covered)],
        ]

        event_table = Table(event_data, colWidths=[2*inch, 4*inch])
        event_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ]))
        elements.append(event_table)
        elements.append(Spacer(1, 15))

        # Financial details
        elements.append(Paragraph('<b>Payment Details</b>', bold_style))
        payment_data = [
            ['Amount per Shift:', f'KES{self.amount_to_be_paid:.2f}'],
            ['Number of Shifts:', str(self.shifts_covered)],
            ['Total Amount:', f'KES{self.total_amount:.2f}'],
        ]

        payment_table = Table(payment_data, colWidths=[2*inch, 4*inch])
        payment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('BACKGROUND', (-1, -1), (-1, -1), colors.lightblue),
            ('FONTNAME', (-1, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(payment_table)
        elements.append(Spacer(1, 15))

        # Notes
        if self.notes:
            elements.append(Paragraph('<b>Additional Notes</b>', bold_style))
            elements.append(Paragraph(self.notes, normal_style))
            elements.append(Spacer(1, 15))

        # Footer
        elements.append(Spacer(1, 30))
        footer_style = ParagraphStyle('footer', parent=styles['Normal'], fontSize=9, textColor=colors.gray, alignment=1)
        elements.append(Paragraph('Thank you for choosing Mookh.com for your event needs.', footer_style))
        elements.append(Paragraph('This invoice was generated on ' + timezone.now().strftime('%B %d, %Y at %H:%M'), footer_style))

        doc.build(elements)
        buffer.seek(0)
        filename = f'invoice_{self.id}.pdf'
        self.pdf_file.save(filename, ContentFile(buffer.read()), save=False)
        buffer.close()


class Report(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    general_report = models.TextField()
    tech_report = models.TextField()
    additional_notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='documents/reports/', null=True, blank=True)

    def __str__(self):
        return f'Report {self.id} for {self.user.username} - {self.event_name}'

    def generate_pdf(self):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=72, bottomMargin=36)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('title', parent=styles['Heading1'], fontSize=24, textColor=colors.darkblue, spaceAfter=20, alignment=1)
        header_style = ParagraphStyle('header', parent=styles['Normal'], fontSize=12, textColor=colors.gray, alignment=1)
        section_style = ParagraphStyle('section', parent=styles['Heading2'], fontSize=14, textColor=colors.darkblue, spaceAfter=10)
        normal_style = ParagraphStyle('normal', parent=styles['Normal'], fontSize=11, leading=16)

        elements = []

        # Header with logo and company info
        logo_path = settings.BASE_DIR / 'invoices' / 'static' / 'invoices' / 'images' / 'mookhlogo.png'
        try:
            if logo_path.exists():
                logo = Image(str(logo_path), width=160, height=60)
                elements.append(logo)
                elements.append(Spacer(1, 10))
        except Exception:
            pass

        elements.append(Paragraph('Mookh.com', header_style))
        elements.append(Paragraph('Professional Event Services', header_style))
        elements.append(Spacer(1, 20))

        # Report title
        elements.append(Paragraph('EVENT REPORT', title_style))
        elements.append(Spacer(1, 20))

        # Report details table
        report_data = [
            ['Report ID:', f'RPT-{self.id:04d}'],
            ['Date:', self.created_at.strftime('%B %d, %Y')],
            ['Submitted by:', self.user.get_full_name() or self.user.username],
            ['Email:', self.user.email],
            ['Phone:', self.user.profile.phone or 'Not provided'],
        ]

        report_table = Table(report_data, colWidths=[2*inch, 4*inch])
        report_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ]))
        elements.append(report_table)
        elements.append(Spacer(1, 20))

        # Event details
        elements.append(Paragraph('<b>Event Information</b>', section_style))
        event_data = [
            ['Event Name:', self.event_name],
            ['Location:', self.location],
        ]

        event_table = Table(event_data, colWidths=[2*inch, 4*inch])
        event_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ]))
        elements.append(event_table)
        elements.append(Spacer(1, 15))

        # General Report
        elements.append(Paragraph('<b>General Report</b>', section_style))
        general_box = Table([[Paragraph(self.general_report, normal_style)]], colWidths=[6.5*inch])
        general_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('BOX', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(general_box)
        elements.append(Spacer(1, 15))

        # Tech Report
        elements.append(Paragraph('<b>Technical Report</b>', section_style))
        tech_box = Table([[Paragraph(self.tech_report, normal_style)]], colWidths=[6.5*inch])
        tech_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('BOX', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(tech_box)
        elements.append(Spacer(1, 15))

        # Additional Notes
        if self.additional_notes:
            elements.append(Paragraph('<b>Additional Notes</b>', section_style))
            notes_box = Table([[Paragraph(self.additional_notes, normal_style)]], colWidths=[6.5*inch])
            notes_box.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
                ('BOX', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('PADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(notes_box)
            elements.append(Spacer(1, 15))

        # Footer
        elements.append(Spacer(1, 30))
        footer_style = ParagraphStyle('footer', parent=styles['Normal'], fontSize=9, textColor=colors.gray, alignment=1)
        elements.append(Paragraph('Report generated by Mookh.com event management system.', footer_style))
        elements.append(Paragraph('Generated on ' + timezone.now().strftime('%B %d, %Y at %H:%M'), footer_style))

        doc.build(elements)
        buffer.seek(0)
        filename = f'report_{self.id}.pdf'
        self.pdf_file.save(filename, ContentFile(buffer.read()), save=False)
        buffer.close()
