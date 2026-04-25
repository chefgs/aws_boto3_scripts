"""Delete an S3 bucket (must be empty first)."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_bucket(client, bucket_name, dry_run=False):
    """Delete the specified S3 bucket."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete bucket: %s", bucket_name)
        return None
    try:
        response = client.delete_bucket(Bucket=bucket_name)
        logger.info("Deleted bucket: %s", bucket_name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete bucket %s: %s", bucket_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete an S3 bucket")
    parser.add_argument("--name", required=True, help="Bucket name to delete")
    args = parser.parse_args()
    client = get_client("s3", args.profile, args.region)
    delete_bucket(client, args.name, args.dry_run)
