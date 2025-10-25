import boto3
from botocore.client import Config
import os
import json
import dotenv

dotenv.load_dotenv()

SCALEWAY_ACCESS_KEY = os.getenv("SCALEWAY_ACCESS_KEY")
SCALEWAY_SECRET_KEY = os.getenv("SCALEWAY_SECRET_KEY")
REGION = os.getenv("REGION", "pl-waw")
BUCKET_NAME = os.getenv("BUCKET_NAME")
REPORT_SOURCE_FILE = os.getenv("REPORT_SOURCE_FILE")

s3 = boto3.client(
    "s3",
    endpoint_url=f"https://s3.{REGION}.scw.cloud",
    aws_access_key_id=SCALEWAY_ACCESS_KEY,
    aws_secret_access_key=SCALEWAY_SECRET_KEY,
    config=Config(signature_version="s3v4")
)

def remove_image_urls(data):
    """
    Recursively remove all 'imageUrl' keys from nested dictionaries and lists
    """
    if isinstance(data, dict):
        return {k: remove_image_urls(v) for k, v in data.items() if k != 'imageUrl'}
    elif isinstance(data, list):
        return [remove_image_urls(item) for item in data]
    else:
        return data

def load_report_from_s3(filename: str = REPORT_SOURCE_FILE) -> dict:
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=filename)
        file_content = response['Body'].read().decode('utf-8')
        data = json.loads(file_content)
        cleaned_data = remove_image_urls(data)
        return cleaned_data
    except Exception as e:
        print(f"Error loading from S3: {e}")
        return {}