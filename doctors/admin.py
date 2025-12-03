from django.contrib import admin
from .models import Doctor

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'phone')
    search_fields = ('name', 'specialty')
    list_filter = ('specialty',)
