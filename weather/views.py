from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .weather_client import get_current_weather, get_forecast_for_date, CityNotFoundError
from .models import ForecastOverride
from .serializers import ForecastOverrideSerializer
from datetime import datetime, timedelta


class CurrentWeatherView(APIView):
    def get(self, request):
        city = request.query_params.get("city")
        if not city:
            return Response({"error": "Missing 'city' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = get_current_weather(city)
            return Response(data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)


class ForecastWeatherView(APIView):
    def get(self, request):
        city = request.query_params.get("city")
        date_str = request.query_params.get("date")

        if not city or not date_str:
            return Response({"error": "Missing 'city' or 'date' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date = datetime.strptime(date_str, "%d.%m.%Y").date()
        except ValueError:
            return Response({"error": "Invalid date format. Expected dd.MM.yyyy"}, status=status.HTTP_400_BAD_REQUEST)

        today = datetime.now().date()
        if date < today or date > today + timedelta(days=10):
            return Response({"error": "Date must be from today up to 10 days ahead"},
                            status=status.HTTP_400_BAD_REQUEST)

        override = ForecastOverride.objects.filter(city__iexact=city, date=date).first()
        if override:
            return Response({
                "min_temperature": override.min_temperature,
                "max_temperature": override.max_temperature
            })

        try:
            data = get_forecast_for_date(city, date)
            return Response(data)
        except CityNotFoundError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            if str(e) == "No forecast data for this date":
                return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
            else:
                # Если ошибка не про отсутствие данных
                return Response({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = ForecastOverrideSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            obj, _ = ForecastOverride.objects.update_or_create(
                city=data["city"],
                date=data["date"],
                defaults={
                    "min_temperature": data["min_temperature"],
                    "max_temperature": data["max_temperature"]
                }
            )
            return Response({"status": "forecast saved"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

