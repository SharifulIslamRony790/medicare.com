from django import forms
from .models import Prescription

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = '__all__'
        widgets = {
            'appointment': forms.Select(attrs={'class': 'form-select'}),
            'medicines': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'advice': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
