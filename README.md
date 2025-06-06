# Weather Forecast API 🌦️

Это REST API для получения текущей погоды и прогноза по городам.  В проекте реализована оптимизация повторных запросов — за счёт модели ForecastOverride, которая сохраняет вручную переопределённый прогноз. Это позволяет не обращаться к внешнему API повторно, если данные на определённую дату и город уже есть. Поддерживается переопределение прогноза вручную и валидация входных данных.
## Источник данных
В проекте используется [OpenWeatherMap API](https://openweathermap.org/api) для получения данных о текущей погоде и прогнозе.
Чтобы запустить проект, вам потребуется собственный API-ключ. Получить его можно бесплатно, зарегистрировавшись на сайте:
```
👉 https://home.openweathermap.org/api_keys
```
После получения ключа добавьте его в файл `.env`(по аналогии с .env.template)

## 📦 Стек технологий (подробно в файле requirements.txt)

- Python 3.12
- Django 5+
- Django REST Framework
- SQLite (по умолчанию, легко заменить на PostgreSQL)
- Pytest

## 🚀 Запуск проекта

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/ribondareva/WeatherApi.git
cd WeatherApi
```
### 2. Установите зависимости
```
python -m venv venv
source venv/bin/activate  # для Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### 3. Создайте файл .env по аналогии с .env.template
### 4. Примените миграции
```
python manage.py migrate
```
### 5. Запустите сервер
```
python manage.py runserver
```
## 📘 Использование API
- Получение текущей погоды (GET)
```
http://127.0.0.1:8000/api/weather/current/?city=London
```

- Получение прогноза погоды (GET)
```
http://127.0.0.1:8000/api/weather/forecast/?city=London&date=12.06.2025
```
- Переопределение прогноза (POST)
```
http://127.0.0.1:8000/api/weather/forecast/
```
```
{
  "city": "London",
  "date": "12.06.2025",
  "min_temperature": 10.5,
  "max_temperature": 15.0
}
```
##  ✅ Тестирование и покрытие кода (покрытие тестами составляет 94%)
- Запустите тесты с замером покрытия
```
coverage run -m pytest
```
- Посмотрите отчет в консоли:
```
coverage report -m
```
- Для более детального отчета в формате HTML:
```
coverage html
```
