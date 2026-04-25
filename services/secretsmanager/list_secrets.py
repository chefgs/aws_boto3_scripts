"""List secrets in AWS Secrets Manager."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_secrets(client):
    """Return a list of secret metadata dicts."""
    try:
        paginator = client.get_paginator("list_secrets")
        secrets = []
        for page in paginator.paginate():
            secrets.extend(page.get("SecretList", []))
        logger.info("Found %d secret(s)", len(secrets))
        return secrets
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list secrets: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List Secrets Manager secrets")
    args = parser.parse_args()
    client = get_client("secretsmanager", args.profile, args.region)
    list_secrets(client)
