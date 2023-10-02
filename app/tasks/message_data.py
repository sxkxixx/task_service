from typing import Literal
from pydantic import EmailStr
from tasks.templates import Template
from email.message import EmailMessage
from core.config import SMTP_EMAIL


class MessageData:
    templates = Template()

    def __init__(self, **kwargs):
        self.__from_addr = kwargs.get('from_addr') or SMTP_EMAIL
        self.__subject: str = kwargs.get('subject')
        self.__recipient_email: EmailStr = kwargs.get('recipient_email')
        self.__template_type: Literal['verify_email', 'password_update'] = kwargs.get('template_type')
        self.__token: str = kwargs.get('token')

    @property
    def template(self) -> str:
        return self.templates[self.__template_type](
            email=self.__recipient_email,
            token=self.__token,
        )

    @property
    def from_add(self):
        return self.__from_addr

    @property
    def subject(self):
        return self.__subject

    @property
    def recipient_email(self):
        return self.__recipient_email

    @property
    def get_message(self):
        message = EmailMessage()
        message['Subject'] = self.__subject
        message['From'] = self.__from_addr
        message['To'] = self.__recipient_email
        message.set_content(
            self.template, subtype='html'
        )
        return message
