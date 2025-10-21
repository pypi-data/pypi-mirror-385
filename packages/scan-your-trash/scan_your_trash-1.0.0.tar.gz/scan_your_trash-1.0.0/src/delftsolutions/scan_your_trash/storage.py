import boto3
import tempfile
import os
import contextlib

def fetch_samples(bucket_name, destination = None, endpoint = "https://landfill.scantrash.de"):
    s3_resource = boto3.resource('s3', endpoint_url=endpoint)
    s3_client = boto3.client('s3', endpoint_url=endpoint)
    bucket = s3_resource.Bucket(bucket_name)

    context = contextlib.nullcontext(destination)
    if destination == None:
        context = tempfile.TemporaryDirectory()

    with context as destfolder:
        for obj in bucket.objects.all():
            destpath = os.path.join(destfolder, obj.key)
            if not os.path.exists(os.path.dirname(destpath)):
                os.makedirs(os.path.dirname(destpath))

            if not os.path.isfile(destpath):
                bucket.download_file(obj.key, destpath)

            yield destpath

            if destination == None:
                pathlib.unlink(destpath)

