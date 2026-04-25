"""List all S3 buckets in the account."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_buckets(client):
    """Return a list of bucket names."""
    try:
        response = client.list_buckets()
        buckets = [b["Name"] for b in response.get("Buckets", [])]
        for name in buckets:
            logger.info("Bucket: %s", name)
        return buckets
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list buckets: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List S3 buckets")
    args = parser.parse_args()
    client = get_client("s3", args.profile, args.region)
    list_buckets(client)
