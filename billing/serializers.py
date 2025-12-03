from rest_framework import serializers
from .models import Invoice

class InvoiceSerializer(serializers.ModelSerializer):
    patient_name = serializers.ReadOnlyField(source='patient.name')

    class Meta:
        model = Invoice
        fields = '__all__'
