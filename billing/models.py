from django.db import models
from patients.models import Patient
from appointments.models import Appointment

class Invoice(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    items = models.TextField(help_text="Description of billed items")
    date = models.DateField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice #{self.id} - {self.patient.name}"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('VISA', 'Visa Card'),
        ('MASTERCARD', 'MasterCard'),
        ('BKASH', 'bKash'),
        ('NAGAD', 'Nagad'),
        ('CASH', 'Cash'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} Payment - {self.transaction_id}"
