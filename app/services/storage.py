import boto3
from botocore.exceptions import ClientError
import logging

class StorageService:
    """S3 storage service"""

    def __init__(self, bucket_name: str = "strategy-optimizer"):
        self.s3 = boto3.client('s3')
        self.bucket_name = bucket_name

    def upload_file(self, file_name: str, object_name: str = None):
        if object_name is None:
            object_name = file_name

        try:
            self.s3.upload_file(file_name, self.bucket_name, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def get_presigned_url(self, object_name: str, expiration: int = 3600):
        try:
            response = self.s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': self.bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
        except ClientError as e:
            logging.error(e)
            return None
        return response
