from datetime import datetime, timedelta
import pytest


@pytest.mark.django_db
def test_get_forecast_real_data(api_client):
    """GET: получение прогноза для существующего города и даты"""
    response = api_client.get("/api/weather/forecast/?city=London&date=10.06.2025")
    assert response.status_code in [200, 404]


@pytest.mark.django_db
def test_post_override_forecast(api_client):
    """POST: добавление оверрайда прогноза"""
    payload = {
        "city": "Paris",
        "date": "10.06.2025",
        "min_temperature": 5.0,
        "max_temperature": 15.0
    }
    response = api_client.post("/api/weather/forecast/", payload, format="json")
    assert response.status_code == 200
    assert response.data["status"] == "forecast saved"


@pytest.mark.django_db
def test_get_returns_override_if_exists(api_client):
    """GET: при наличии override возвращается он, а не прогноз"""
    payload = {
        "city": "Paris",
        "date": "10.06.2025",
        "min_temperature": 5.0,
        "max_temperature": 15.0
    }
    api_client.post("/api/weather/forecast/", payload, format="json")
    response = api_client.get("/api/weather/forecast/?city=Paris&date=10.06.2025")
    assert response.status_code == 200
    assert response.data["min_temperature"] == 5.0


@pytest.mark.django_db
def test_override_forecast_overwrites_existing(api_client):
    """POST: повторная отправка должна обновить override"""
    payload1 = {"city": "Rome", "date": "12.06.2025", "min_temperature": 7.0, "max_temperature": 17.0}
    payload2 = {"city": "Rome", "date": "12.06.2025", "min_temperature": 10.0, "max_temperature": 20.0}

    api_client.post("/api/weather/forecast/", payload1, format="json")
    api_client.post("/api/weather/forecast/", payload2, format="json")

    response = api_client.get("/api/weather/forecast/?city=Rome&date=12.06.2025")
    assert response.data["min_temperature"] == 10.0


@pytest.mark.django_db
def test_override_city_case_insensitive(api_client):
    """GET: override работает при разных регистрах города"""
    payload = {"city": "Paris", "date": "10.06.2025", "min_temperature": 5.0, "max_temperature": 15.0}
    api_client.post("/api/weather/forecast/", payload, format="json")
    response = api_client.get("/api/weather/forecast/?city=paris&date=10.06.2025")
    assert response.status_code == 200


@pytest.mark.django_db
def test_post_forecast_duplicate_data_returns_success(api_client):
    """POST: одинаковые данные не вызывают ошибку"""
    payload = {"city": "Berlin", "date": "11.06.2025", "min_temperature": 6.0, "max_temperature": 16.0}
    r1 = api_client.post("/api/weather/forecast/", payload, format="json")
    r2 = api_client.post("/api/weather/forecast/", payload, format="json")
    assert r1.status_code == 200
    assert r2.status_code == 200


@pytest.mark.django_db
def test_validation_error_on_wrong_date_format(api_client):
    """POST: ошибка валидации при неверном формате даты"""
    payload = {"city": "Paris", "date": "2025-06-10", "min_temperature": 5.0, "max_temperature": 15.0}
    response = api_client.post("/api/weather/forecast/", payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_validation_error_on_min_temp_greater_than_max(api_client):
    """POST: min_temperature не может быть выше max_temperature"""
    payload = {"city": "Paris", "date": "10.06.2025", "min_temperature": 20.0, "max_temperature": 15.0}
    response = api_client.post("/api/weather/forecast/", payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_forecast_not_found_for_invalid_city(api_client):
    """GET: ошибка для несуществующего города"""
    response = api_client.get("/api/weather/forecast/?city=NotFoundCity&date=10.06.2025")
    assert response.status_code in [400, 404]


@pytest.mark.django_db
def test_get_forecast_missing_parameters(api_client):
    """GET: обязательные параметры city и date"""
    assert api_client.get("/api/weather/forecast/").status_code == 400
    assert api_client.get("/api/weather/forecast/?city=Paris").status_code == 400
    assert api_client.get("/api/weather/forecast/?date=10.06.2025").status_code == 400


@pytest.mark.django_db
def test_get_forecast_date_out_of_range(api_client):
    """GET: дата должна быть в пределах 0–10 дней от текущей"""
    today = datetime.now().date()

    past = (today - timedelta(days=1)).strftime("%d.%m.%Y")
    future = (today + timedelta(days=11)).strftime("%d.%m.%Y")

    # дата в прошлом
    assert api_client.get(f"/api/weather/forecast/?city=Paris&date={past}").status_code == 400
    # дата слишком далеко в будущем
    assert api_client.get(f"/api/weather/forecast/?city=Paris&date={future}").status_code == 400


@pytest.mark.django_db
def test_post_empty_payload(api_client):
    """POST: пустое тело запроса — ошибка"""
    response = api_client.post("/api/weather/forecast/", {}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_get_forecast_value_error_unexpected(api_client, mocker):
    """GET: внутренний ValueError в get_forecast_for_date"""
    mocker.patch("weather.views.get_forecast_for_date", side_effect=ValueError("unexpected error"))
    response = api_client.get("/api/weather/forecast/?city=Paris&date=10.06.2025")
    assert response.status_code == 400


@pytest.mark.django_db
def test_override_forecast_partial_update_not_allowed(api_client):
    """PATCH: метод не поддерживается"""
    payload = {"city": "Rome", "date": "12.06.2025", "min_temperature": 10.0}
    response = api_client.patch("/api/weather/forecast/", payload, format="json")
    assert response.status_code in [405, 400]


@pytest.mark.django_db
def test_post_forecast_equal_min_and_max(api_client):
    payload = {
        "city": "Berlin",
        "date": "12.06.2025",
        "min_temperature": 15.5,
        "max_temperature": 15.5
    }
    response = api_client.post("/api/weather/forecast/", payload, format="json")
    assert response.status_code == 200
