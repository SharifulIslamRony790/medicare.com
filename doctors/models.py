from django.db import models
from django.conf import settings

class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='doctor_profile')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    specialty = models.CharField(max_length=100)
    available_days = models.CharField(max_length=200, help_text="Comma-separated days, e.g., Mon,Tue,Wed")
    image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.image:
            from medicare_core.utils import generate_profile_image
            img_content = generate_profile_image(self.name)
            if img_content:
                self.image.save(f"{self.name}_profile.png", img_content, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.specialty}"
