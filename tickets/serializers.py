from rest_framework import serializers
from datetime import date
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['user', 'location', 'date', 'quantity', 'amount']

    def validate_date(self, data):
        current_date = date.today()
        if (data < current_date):
            raise serializers.ValidationError("Select a future date.")
        return data

    def validate_amount(self, data):
        if data < 9:
            raise serializers.ValidationError(
                "Amount needs to be more than 9.00 Rs")
        return data
