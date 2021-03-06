import boto3
import pandas as pd
from typing import List
from io import BytesIO
from app.settings import settings


s3 = boto3.client(
    's3',
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key
)


def backup(workouts: List[dict], timestamp: str):
    """ Backup the workout dictionary from the scraper, use the filename"""
    buffer = BytesIO()
    df = pd.DataFrame(workouts)
    df.to_parquet(buffer, index=False)

    try:
        s3.put_object(Bucket=settings.aws_bucket_name, Key=f'{timestamp}.parquet', Body=buffer.getvalue())
        print(f'Successfully uploaded "{timestamp}.parquet" to S3')

    except Exception as e:
        print(f'S3 upload exception: {e}')
