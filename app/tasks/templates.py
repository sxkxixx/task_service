from core.config import ORIGIN


class Template:
    @staticmethod
    def USER_VERIFY_TEMPLATE(**kwargs) -> str:
        return f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head><meta charset="UTF-8"></head>
        <body>
            <h1>Здравствуйте, {kwargs.get('email')}</h1>
            <h2>Чтобы верифицировать свой аккаунт, перейдите по <a href="{ORIGIN}/verify_user?token={kwargs.get('token')}">ссылке</a>
            </h2>
        </body>
        </html>
        """

    @staticmethod
    def USER_PASSWORD_UPD_TEMPLATE(**kwargs) -> str:
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head><meta charset="UTF-8"></head>
        <body>
            <h1>Здравствуйте, {kwargs.get('email')}</h1>
            <h2>Для смены пароля необходимо перейти по 
                <a href="http://localhost:8000/password_refresh?token={kwargs.get('token')}">
                ссылке
                </a>
            </h2>
        </body>
        </html>
        """

    def __getitem__(self, item):
        templates = {
            'verify_email': lambda **kwargs: self.USER_VERIFY_TEMPLATE(**kwargs),
            'password_update': lambda **kwargs: self.USER_PASSWORD_UPD_TEMPLATE(**kwargs)
        }
        return templates[item]
