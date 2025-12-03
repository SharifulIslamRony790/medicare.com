from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework import viewsets
from .models import Prescription
from .serializers import PrescriptionSerializer
from .forms import PrescriptionForm
from appointments.models import Appointment
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from io import BytesIO

# API ViewSet
class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

# UI Views
@login_required
def prescription_list(request):
    # Filter to show only logged-in user's prescriptions
    if hasattr(request.user, 'patient_profile'):
        prescriptions = Prescription.objects.filter(appointment__patient=request.user.patient_profile).order_by('-created_at')
    else:
        # Admin/staff can see all prescriptions
        prescriptions = Prescription.objects.all().order_by('-created_at')
    return render(request, 'prescription_list.html', {'prescriptions': prescriptions})

@login_required
def prescription_add(request):
    # Only doctors can create prescriptions
    if request.user.role != 'doctor':
        return HttpResponseForbidden("Only doctors can write prescriptions.")
        
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            # Auto-set doctor if logged in as doctor
            if hasattr(request.user, 'doctor_profile'):
                # Ensure the appointment belongs to this doctor
                if prescription.appointment.doctor != request.user.doctor_profile:
                     return HttpResponseForbidden("You can only write prescriptions for your own appointments.")
            prescription.save()
            return redirect('prescription_list')
    else:
        form = PrescriptionForm()
        # If doctor, filter appointments to only show their completed appointments
        if hasattr(request.user, 'doctor_profile'):
            form.fields['appointment'].queryset = Appointment.objects.filter(
                doctor=request.user.doctor_profile, 
                status='completed'
            ).order_by('-date')
            
    return render(request, 'prescription_form.html', {'form': form})

@login_required
def prescription_pdf(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    
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
    elements.append(Paragraph("MediCare Prescription", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Patient and Doctor Info
    info_data = [
        ['Patient:', prescription.appointment.patient.name, 'Date:', prescription.created_at.strftime('%Y-%m-%d')],
        ['Doctor:', prescription.appointment.doctor.name, 'Time:', prescription.created_at.strftime('%H:%M')],
    ]
    
    info_table = Table(info_data, colWidths=[1*inch, 2.5*inch, 1*inch, 1.5*inch])
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
    
    # Medicines
    elements.append(Paragraph("<b>Medicines:</b>", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(prescription.medicines.replace('\n', '<br/>'), styles['BodyText']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Advice
    if prescription.advice:
        elements.append(Paragraph("<b>Advice:</b>", styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(prescription.advice.replace('\n', '<br/>'), styles['BodyText']))
    
    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="prescription_{pk}.pdf"'
    response.write(pdf)
    
    return response
