# google cloud bucket

import os
from dotenv import load_dotenv

from google.cloud import storage
from google.oauth2 import service_account

load_dotenv()

# env variables
BUCKET_NAME = os.getenv('BUCKET_NAME')
PROJECT_NAME = os.getenv('PROJECT_NAME')

"""
Set up Google cloud client, bucket and authentication
"""


credentials = service_account.Credentials.from_service_account_file('service_account.json')

client = storage.Client(credentials=credentials, project=PROJECT_NAME)

# get cloud bucket using URL
bucket = client.get_bucket(BUCKET_NAME)


# upload blob to google cloud
def upload_blob(source_file_name, destination_blob_name):
    """
    Path to the file to upload
    source_file_name = "local/path/to/file"
    :param source_file_name:

    ID of the object
    destination_blob_name = "storage-object-name"
    :param destination_blob_name:
    """
    blob = bucket.blob(destination_blob_name)

    return blob.upload_from_file(source_file_name)


# download blob from google cloud
def download_blob(source_blob_name, destination_file_name):
    """
    ID of the object
    source_blob_name = "storage-object-name"
    :param source_blob_name:

    The path to which the file should be downloaded
    destination_file_name = "local/path/to/file"
    :param destination_file_name:
    """
    blob = bucket.blob(source_blob_name)

    return blob.download_to_file(destination_file_name)


# get the public url for an image from within the bucket
def get_image_url(source_blob_name):
    url = f"https://storage.googleapis.com/{BUCKET_NAME}/{source_blob_name}"
    return url
