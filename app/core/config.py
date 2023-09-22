from dotenv import load_dotenv
import os

load_dotenv()

# Database
SQL_DATABASE: str = os.getenv('SQL_DATABASE')
SQL_HOST: str = os.getenv('SQL_HOST')
SQL_PORT: int = int(os.getenv('SQL_PORT'))
SQL_USER: str = os.getenv('SQL_USER')
SQL_PASSWORD: str = os.getenv('SQL_PASSWORD')

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

FILE_LINKS_DOMAIN = [
    'https://docs.google.com',
    'https://drive.google.com',
    'https://disk.yandex.ru',
]
