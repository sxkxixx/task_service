import aioboto3
from core.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME, REGION_NAME
import os
from fastapi import File, UploadFile


class S3Service:
    session = aioboto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=REGION_NAME,
    )
    service_name = 's3'
    endpoint_url = 'https://storage.yandexcloud.net'

    async def upload_file(self, file: UploadFile = File(...)):
        async with self.session.client(self.service_name, endpoint_url=self.endpoint_url) as client:
            unique_filename = self.__generate_unique_filename(file.filename)
            await client.upload_fileobj(file, BUCKET_NAME, unique_filename)
        return unique_filename

    async def get_presigned_url(self, file_name):
        async with self.session.client(self.service_name, endpoint_url=self.endpoint_url) as client:
            url = await client.generate_presigned_url(
                'get_object',
                Params={"Bucket": BUCKET_NAME, "Key": file_name},
                ExpiresIn=300
            )
        return url

    async def delete_file(self, file_name):
        async with self.session.client(self.service_name, endpoint_url=self.endpoint_url) as client:
            response = await client.delete_object(Bucket=BUCKET_NAME, Key=file_name)
        return response

    async def change_files(self, previous_file_name: str, current_file: UploadFile = File(...)):
        async with self.session.client(self.service_name, endpoint_url=self.endpoint_url) as client:
            await client.delete_object(Bucket=BUCKET_NAME, Key=previous_file_name)
            unique_filename = self.__generate_unique_filename(current_file.filename)
            await client.upload_fileobj(current_file, BUCKET_NAME, unique_filename)
        return unique_filename

    async def __get_client_session(self):
        # TODO: Хуй знает, не работает
        async with self.session.client(self.service_name, endpoint_url=self.endpoint_url) as client:
            print(type(client))
            yield client

    @staticmethod
    def __generate_unique_filename(previous_filename: str):
        extension = previous_filename[previous_filename.rfind('.') + 1:]
        return f'{os.urandom(16).hex()}.{extension}'
