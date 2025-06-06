from rest_framework import serializers
from datetime import datetime, timedelta


class ForecastOverrideSerializer(serializers.Serializer):
    city = serializers.CharField()
    date = serializers.DateField(input_formats=["%d.%m.%Y"])
    min_temperature = serializers.FloatField()
    max_temperature = serializers.FloatField()

    def validate(self, data):
        if data["min_temperature"] > data["max_temperature"]:
            raise serializers.ValidationError("min_temperature cannot be greater than max_temperature")

        today = datetime.now().date()
        if data["date"] < today:
            raise serializers.ValidationError("Date cannot be in the past")
        if data["date"] > today + timedelta(days=10):
            raise serializers.ValidationError("Date cannot be more than 10 days in the future")

        return data
