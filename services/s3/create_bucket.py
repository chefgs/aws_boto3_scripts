"""Create one or more S3 buckets."""
import logging
import random

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_bucket(client, bucket_name, region):
    """Create a single S3 bucket and return the response."""
    try:
        if region == "us-east-1":
            response = client.create_bucket(Bucket=bucket_name)
        else:
            response = client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )
        logger.info("Created bucket: %s", bucket_name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create bucket %s: %s", bucket_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create S3 bucket(s)")
    parser.add_argument("--prefix", default="boto3bucket", help="Bucket name prefix")
    parser.add_argument("--count", type=int, default=1, help="Number of buckets")
    args = parser.parse_args()

    client = get_client("s3", args.profile, args.region)
    for _ in range(args.count):
        name = args.prefix + str(random.randint(0, 99999))
        create_bucket(client, name, args.region)
