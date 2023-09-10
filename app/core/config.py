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
ACCESS_TOKEN_TTL_MINUTES: int = 5
REFRESH_TOKEN_TTL_DAYS: int = 60
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


FILE_LINKS_DOMAIN = [
    'https://docs.google.com',
    'https://drive.google.com',
    'https://disk.yandex.ru',
]
