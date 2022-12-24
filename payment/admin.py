from django.contrib import admin
from .models import Payment

# Register your models here.


class PaymentAdmin(admin.ModelAdmin):
    readonly_fields = ['id']


admin.site.register(Payment, PaymentAdmin)
