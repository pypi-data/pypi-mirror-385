import logging
import os
import tarfile
import tempfile

import boto3
from baseten_shared.blobs.types import S3BlobWithCredentials
from boto3.s3.transfer import TransferConfig
from tqdm import tqdm


logger = logging.getLogger(__name__)


def multipart_upload_boto3(file_path, blob_with_creds: S3BlobWithCredentials):
    s3_resource = boto3.resource("s3", **blob_with_creds.credentials.model_dump())
    filesize = os.stat(file_path).st_size

    with tqdm(total=filesize, desc="Upload", unit="B", ncols=60, unit_scale=True) as pbar:
        s3_resource.Object(blob_with_creds.s3_bucket, blob_with_creds.s3_key).upload_file(
            file_path,
            Config=TransferConfig(max_concurrency=10, use_threads=True),
            Callback=pbar.update,
        )


def archive_truss(truss_dir):
    logger.info("Archiving %s", truss_dir)
    # Keeping the suffix as .tgz for backwards compat but this archive is uncompressed
    # to optimize for upload speed since compression is not effective for most trusses.
    temp_file = tempfile.NamedTemporaryFile(suffix=".tgz")
    with tarfile.open(temp_file.name, "w:") as tar:
        tar.add(truss_dir, arcname=".")
    temp_file.file.seek(0)
    return temp_file
