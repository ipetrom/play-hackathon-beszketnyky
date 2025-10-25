import boto3
from botocore.client import Config
import os
import dotenv

dotenv.load_dotenv()

SCALEWAY_ACCESS_KEY = os.getenv("SCALEWAY_ACCESS_KEY")
SCALEWAY_SECRET_KEY = os.getenv("SCALEWAY_SECRET_KEY")
REGION = os.getenv("REGION", "pl-waw")
BUCKET_NAME = os.getenv("BUCKET_NAME")

s3 = boto3.client(
    "s3",
    endpoint_url=f"https://s3.{REGION}.scw.cloud",
    aws_access_key_id=SCALEWAY_ACCESS_KEY,
    aws_secret_access_key=SCALEWAY_SECRET_KEY,
    config=Config(signature_version="s3v4")
)

def list_files():
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    if "Contents" in response:
        for obj in response["Contents"]:
            print(obj["Key"])
    else:
        print("Бакет пустой")

def upload_file(local_file, s3_key):
    s3.upload_file(local_file, BUCKET_NAME, s3_key)
    print(f"Файл {local_file} загружен как {s3_key}")

def download_file(s3_key, local_file):
    s3.download_file(BUCKET_NAME, s3_key, local_file)
    print(f"Файл {s3_key} скачан в {local_file}")

if __name__ == "__main__":
    list_files()

    with open("example.txt", "w") as f:
        f.write("Hello S3")
    upload_file("example.txt", "example.txt")

    download_file("example.txt", "downloaded_example.txt")
