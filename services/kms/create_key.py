"""Create one or more KMS keys."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_key(client, description="boto3-managed key"):
    """Create a KMS key and return the key metadata."""
    try:
        response = client.create_key(
            Description=description,
            Origin="AWS_KMS",
            Tags=[{"TagKey": "ManagedBy", "TagValue": "boto3-scripts"}],
        )
        key_id = response["KeyMetadata"]["KeyId"]
        logger.info("Created KMS key: %s", key_id)
        return response["KeyMetadata"]
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create KMS key: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create KMS key(s)")
    parser.add_argument(
        "--description", default="boto3-managed key", help="Key description"
    )
    parser.add_argument("--count", type=int, default=1, help="Number of keys")
    args = parser.parse_args()
    client = get_client("kms", args.profile, args.region)
    for _ in range(args.count):
        create_key(client, args.description)
