import boto3
from dotenv import load_dotenv
import os

load_dotenv(".env")

resource = boto3.resource('s3',
  endpoint_url = 'https://0e945a75a983d57d44343fd58e36c2d9.r2.cloudflarestorage.com',
  aws_access_key_id = os.getenv("AWS_ACCESS_KEY"),
  aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
)

client = boto3.client('s3',
  endpoint_url = 'https://0e945a75a983d57d44343fd58e36c2d9.r2.cloudflarestorage.com',
  aws_access_key_id = os.getenv("AWS_ACCESS_KEY"),
  aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
)