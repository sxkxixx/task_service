from dotenv import load_dotenv
import os


load_dotenv()

SQL_DATABASE: str = os.getenv('SQL_DATABASE')
SQL_HOST: str = os.getenv('SQL_HOST')
SQL_PORT: int = int(os.getenv('SQL_PORT'))
SQL_USER: str = os.getenv('SQL_USER')
SQL_PASSWORD: str = os.getenv('SQL_PASSWORD')
SECRET_KEY: str = os.getenv('SECRET_KEY')
ACCESS_TOKEN_TTL_MINUTES: int = 120
REFRESH_TOKEN_TTL_DAYS: int = 60
ALGORITHM: str = os.getenv('ALGORITHM')

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION_NAME = os.getenv('REGION_NAME')
BUCKET_NAME = os.getenv('BUCKET_NAME')
