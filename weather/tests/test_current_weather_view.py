import pytest


@pytest.mark.django_db
def test_current_weather_missing_city(api_client):
    """GET: обязательный параметр city"""
    response = api_client.get("/api/weather/current/")
    assert response.status_code == 400


@pytest.mark.django_db
def test_current_weather_city_not_found(api_client, mocker):
    """GET: mock-ошибка — город не найден"""
    mocker.patch("weather.views.get_current_weather", side_effect=ValueError("City not found"))
    response = api_client.get("/api/weather/current/?city=UnknownCity")
    assert response.status_code == 404


@pytest.mark.django_db
def test_current_weather_success(api_client, mocker):
    """GET: успешный ответ от get_current_weather"""
    data = {"city": "Paris", "temperature": 20}
    mocker.patch("weather.views.get_current_weather", return_value=data)
    response = api_client.get("/api/weather/current/?city=Paris")
    assert response.status_code == 200
    assert response.data == data
