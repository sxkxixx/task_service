from core.config import SMTP_EMAIL, SMTP_SERVER, SMTP_PASSWORD, SMTP_PORT
from core.config import REDIS_PORT, REDIS_HOST
from tasks.message_data import MessageData
import smtplib
import celery

REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'

celery_app = celery.Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)


@celery_app.task
def send_email_task(data: MessageData):
    server = smtplib.SMTP_SSL(host=SMTP_SERVER, port=SMTP_PORT)
    server.login(SMTP_EMAIL, SMTP_PASSWORD)
    server.send_message(data.get_message)
    server.close()
