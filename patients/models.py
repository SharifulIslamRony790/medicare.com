from django.db import models
from django.conf import settings

class Patient(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='patient_profile')
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=254, blank=True, null=True)
    address = models.TextField()
    medical_history = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='patients/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.image:
            from medicare_core.utils import generate_profile_image
            img_content = generate_profile_image(self.name)
            if img_content:
                self.image.save(f"{self.name}_profile.png", img_content, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
