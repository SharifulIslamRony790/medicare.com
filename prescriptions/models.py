from django.db import models
from appointments.models import Appointment

class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription')
    medicines = models.TextField(help_text="List of medicines with dosage")
    advice = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.appointment}"
