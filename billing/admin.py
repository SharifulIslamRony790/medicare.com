from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'amount', 'date', 'is_paid')
    list_filter = ('is_paid', 'date')
