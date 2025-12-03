from django import forms
from .models import Invoice

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = '__all__'
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'appointment': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'items': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
