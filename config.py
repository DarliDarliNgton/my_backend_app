import os
from dotenv import load_dotenv
from urllib.parse import quote
from datetime import timedelta

load_dotenv()

class Config:
    # Секретный ключ приложения
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-very-strong-secret-key-here'

    # Конфигурация базы данных
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'postgresql://user:password@localhost:5432/electronics_shop'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Конфигурация JWT
    JWT_SECRET_KEY = SECRET_KEY  # Используем тот же секретный ключ
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)  # Уменьшено для тестирования
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)    # Refresh токен на 30 дней
    JWT_TOKEN_LOCATION = ['headers']  # Используем только заголовки
    JWT_HEADER_NAME = 'Authorization'  # Имя заголовка
    JWT_HEADER_TYPE = 'Bearer'  # Тип токена
    JWT_COOKIE_CSRF_PROTECT = False  # Отключаем CSRF защиту
    PROPAGATE_EXCEPTIONS = True  # Прокидываем исключения

    # Настройки почты
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@example.com')

    # Фикс для кодировки пароля в URL базы данных
    if SQLALCHEMY_DATABASE_URI and '%' in SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = quote(SQLALCHEMY_DATABASE_URI, safe=':/?&=')