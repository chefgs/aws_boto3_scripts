"""List IAM roles."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_roles(client):
    """Return a list of IAM role dicts."""
    try:
        paginator = client.get_paginator("list_roles")
        roles = []
        for page in paginator.paginate():
            roles.extend(page.get("Roles", []))
        for role in roles:
            logger.info("Role: %s (%s)", role["RoleName"], role["Arn"])
        return roles
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list IAM roles: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List IAM roles")
    args = parser.parse_args()
    client = get_client("iam", args.profile, args.region)
    list_roles(client)
