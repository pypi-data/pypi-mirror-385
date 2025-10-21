import logging
import tempfile
from contextlib import contextmanager

import boto3
import yaml
from botocore.exceptions import ClientError
from django.conf import settings

from oracles.truss.truss_transfer import archive_truss, multipart_upload_boto3
from oracles.utilities.s3_utils import (
    create_model_blob_upload_credentials,
    s3_key_for_org_variables,
)


logger = logging.getLogger(__name__)


def upload_truss_to_s3(truss, org_id):
    model_file = archive_truss(truss)
    blob_with_creds = create_model_blob_upload_credentials(org_id)
    multipart_upload_boto3(model_file.name, blob_with_creds)
    return blob_with_creds.s3_key


def upload_variables(variables: dict, org_id):
    s3_client = boto3.client("s3")
    s3_key = s3_key_for_org_variables(org_id)
    with (
        _log_for_client_error(f"uploading variables to s3 for org {org_id}"),
        tempfile.NamedTemporaryFile("w") as tmp_file,
    ):
        # TODO(pankaj)  We shouldn't have to create a temporary file here, but
        # open-telemtry instrumentation is not playing well with boto s3
        # put_object api, so this is a temporary workaroud. We should remove
        # this once we've upgraded open-telemetry instrumentation to get rid of
        # that issue, and switch to passing variables yaml content directly to
        # s3_client.put_object.
        yaml.safe_dump(variables, tmp_file)
        tmp_file.seek(0)
        s3_client.upload_file(tmp_file.name, settings.S3_USER_MODELS_BUCKET_NAME, s3_key)
        return s3_key


@contextmanager
def _log_for_client_error(error_msg: str):
    try:
        yield
    except ClientError as exc:
        logger.warning(f"Error {error_msg}: {exc}")
        raise exc
