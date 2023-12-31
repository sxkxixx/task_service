from dotenv import load_dotenv
import os

load_dotenv()

# Database
POSTGRES_DB: str = os.getenv('POSTGRES_DB')
POSTGRES_HOST: str = os.getenv('POSTGRES_HOST')
POSTGRES_PORT: int = int(os.getenv('POSTGRES_PORT'))
POSTGRES_USER: str = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')

# Auth
SECRET_KEY: str = os.getenv('SECRET_KEY')
ACCESS_TOKEN_TTL_MINUTES: int = 180
REFRESH_TOKEN_TTL_DAYS: int = 60
MESSAGE_TOKEN_TTL_SECONDS: int = 120
ALGORITHM: str = os.getenv('ALGORITHM')

# S3 Storage
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION_NAME = os.getenv('REGION_NAME')
BUCKET_NAME = os.getenv('BUCKET_NAME')

# Redis
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_USER = os.getenv('REDIS_USER')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

REDIS_MESSAGE_CHANNEL = os.getenv('REDIS_PASSWORD') or 'msg'
REFRESH_SESSION_KEY = os.getenv('REFRESH_SESSION_KEY') or 'refresh_session'
MESSAGE_TOKEN_KEY = os.getenv('MESSAGE_TOKEN_KEY') or 'message_token'

SMTP_EMAIL: str = os.getenv('SMTP_EMAIL')
SMTP_PASSWORD: str = os.getenv('SMTP_PASSWORD')
SMTP_SERVER: str = os.getenv('SMTP_SERVER')
SMTP_PORT: int = int(os.getenv('SMTP_PORT'))

ORIGIN = 'http://localhost:8000'

FILE_LINKS_DOMAIN = [
    'https://docs.google.com',
    'https://drive.google.com',
    'https://disk.yandex.ru',
]
