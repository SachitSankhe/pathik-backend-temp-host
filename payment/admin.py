from django.contrib import admin
from .models import Payment

# Register your models here.


class PaymentAdmin(admin.ModelAdmin):
    readonly_fields = ['ID']


admin.site.register(Payment, PaymentAdmin)
