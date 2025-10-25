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
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)
        if "Contents" in response:
            for obj in response["Contents"]:
                print(obj["Key"])
        else:
            print("Bucket is empty")
    except Exception as e:
        print(f"Error listing files: {e}")

def upload_file(local_file, s3_key):
    try:
        s3.upload_file(local_file, BUCKET_NAME, s3_key)
        print(f"File {local_file} uploaded as {s3_key}")
        return True
    except Exception as e:
        print(f"Error uploading file {local_file}: {e}")
        return False

def download_file(s3_key, local_file):
    try:
        s3.download_file(BUCKET_NAME, s3_key, local_file)
        print(f"File {s3_key} downloaded to {local_file}")
        return True
    except Exception as e:
        print(f"Error downloading file {s3_key}: {e}")
        return False

if __name__ == "__main__":
    list_files()

    with open("example.txt", "w") as f:
        f.write("Hello S3")
    upload_file("example.txt", "example.txt")

    download_file("example.txt", "downloaded_example.txt")
