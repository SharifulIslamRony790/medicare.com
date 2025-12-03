from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework import viewsets
from .models import Invoice, Payment
from .serializers import InvoiceSerializer
from .forms import InvoiceForm
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO

from django.core.mail import send_mail
from django.conf import settings

# API ViewSet
class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

# UI Views
@login_required
def invoice_list(request):
    # Filter to show only logged-in user's invoices
    if hasattr(request.user, 'patient_profile'):
        invoices = Invoice.objects.filter(patient=request.user.patient_profile).order_by('-date')
    else:
        # Admin/staff can see all invoices
        invoices = Invoice.objects.all().order_by('-date')
    return render(request, 'invoice_list.html', {'invoices': invoices})

@login_required
def invoice_add(request):
    # Only admin/superuser/staff can create invoices
    if not (request.user.is_superuser or request.user.role in ['admin', 'staff']):
        return HttpResponseForbidden("You don't have permission to create invoices.")
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('invoice_list')
    else:
        form = InvoiceForm()
    return render(request, 'invoice_form.html', {'form': form})

def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'invoice_detail.html', {'invoice': invoice})

@login_required
def payment_select(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    
    # Only the patient who owns the invoice can pay
    if hasattr(request.user, 'patient_profile'):
        if invoice.patient != request.user.patient_profile:
            return HttpResponseForbidden("You can only pay your own invoices.")
    else:
        return HttpResponseForbidden("Only patients can pay invoices.")
    
    if invoice.is_paid:
        return redirect('invoice_detail', pk=invoice_id)
    return render(request, 'payment_select.html', {'invoice': invoice})

@login_required
def payment_process(request, invoice_id, method):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    
    # Only the patient who owns the invoice can pay
    if hasattr(request.user, 'patient_profile'):
        if invoice.patient != request.user.patient_profile:
            return HttpResponseForbidden("You can only pay your own invoices.")
    else:
        return HttpResponseForbidden("Only patients can pay invoices.")
    
    if request.method == 'POST':
        # Simulate payment processing
        transaction_id = str(uuid.uuid4())
        Payment.objects.create(
            invoice=invoice,
            method=method.upper(),
            transaction_id=transaction_id,
            amount=invoice.amount
        )
        invoice.is_paid = True
        invoice.save()

        # Send Email Notification TO User
        # Get user from patient profile
        patient_user = invoice.patient.user
        if patient_user and patient_user.email:
            subject = 'Payment Confirmed - MediCare'
            message = f"""
            Dear {patient_user.username},

            Your payment has been successfully processed.

            Invoice ID: #{invoice.id}
            Amount: ${invoice.amount}
            Transaction ID: {transaction_id}
            Payment Method: {method.upper()}

            Thank you for choosing MediCare.
            """
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [patient_user.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error sending email: {e}")

        return redirect('payment_success', invoice_id=invoice.id)
    
    context = {
        'invoice': invoice,
        'method': method,
        'method_name': dict(Payment.PAYMENT_METHODS).get(method.upper(), method)
    }
    return render(request, 'payment_process.html', context)

@login_required
def payment_success(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    
    # Only the patient who owns the invoice can view payment success
    if hasattr(request.user, 'patient_profile'):
        if invoice.patient != request.user.patient_profile:
            return HttpResponseForbidden("You can only view your own payment receipts.")
    else:
        return HttpResponseForbidden("Only patients can view payment receipts.")
    
    payment = invoice.payments.last()
    return render(request, 'payment_success.html', {'invoice': invoice, 'payment': payment})

@login_required
def payment_receipt_pdf(request, payment_id):
    payment = get_object_or_404(Payment, pk=payment_id)
    invoice = payment.invoice
    
    # Create PDF buffer
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30,
        alignment=1
    )
    
    # Title
    elements.append(Paragraph("Payment Receipt", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Receipt Info
    info_data = [
        ['Receipt #:', str(payment.id), 'Date:', payment.timestamp.strftime('%Y-%m-%d')],
        ['Transaction ID:', payment.transaction_id, 'Time:', payment.timestamp.strftime('%H:%M')],
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 2*inch, 1*inch, 1.5*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e5e7eb')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#e5e7eb')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db'))
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Patient Info
    elements.append(Paragraph("<b>Patient Information:</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))
    
    patient_data = [
        ['Name:', invoice.patient.name],
        ['Phone:', invoice.patient.phone],
    ]
    
    patient_table = Table(patient_data, colWidths=[1.5*inch, 4.5*inch])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    elements.append(patient_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Payment Details
    elements.append(Paragraph("<b>Payment Details:</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))
    
    payment_data = [
        ['Invoice ID:', f'#{invoice.id}'],
        ['Items:', invoice.items],
        ['Payment Method:', payment.get_method_display()],
        ['Amount Paid:', f'${payment.amount}'],
    ]
    
    payment_table = Table(payment_data, colWidths=[1.5*inch, 4.5*inch])
    payment_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#dbeafe')),
    ]))
    
    elements.append(payment_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    elements.append(Paragraph("<i>Thank you for choosing MediCare!</i>", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="receipt_{payment_id}.pdf"'
    response.write(pdf)
    
    return response
