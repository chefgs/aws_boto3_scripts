"""List IAM users."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_users(client):
    """Return a list of IAM user dicts."""
    try:
        paginator = client.get_paginator("list_users")
        users = []
        for page in paginator.paginate():
            users.extend(page.get("Users", []))
        for user in users:
            logger.info("User: %s (%s)", user["UserName"], user["Arn"])
        return users
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list IAM users: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List IAM users")
    args = parser.parse_args()
    client = get_client("iam", args.profile, args.region)
    list_users(client)
