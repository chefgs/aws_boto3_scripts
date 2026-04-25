"""List KMS keys."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_keys(client):
    """Return a list of KMS key IDs."""
    try:
        paginator = client.get_paginator("list_keys")
        keys = []
        for page in paginator.paginate():
            keys.extend(page.get("Keys", []))
        for key in keys:
            logger.info("KMS Key: %s", key["KeyId"])
        return keys
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list KMS keys: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List KMS keys")
    args = parser.parse_args()
    client = get_client("kms", args.profile, args.region)
    list_keys(client)
