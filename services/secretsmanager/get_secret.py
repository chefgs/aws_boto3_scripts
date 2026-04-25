"""Retrieve a secret value from AWS Secrets Manager."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def get_secret(client, name):
    """Retrieve and return the secret string for the given secret name."""
    try:
        response = client.get_secret_value(SecretId=name)
        secret = response.get("SecretString") or response.get("SecretBinary")
        logger.info("Retrieved secret: %s", name)
        return secret
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to get secret %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Retrieve a Secrets Manager secret")
    parser.add_argument("--name", required=True, help="Secret name or ARN")
    args = parser.parse_args()
    client = get_client("secretsmanager", args.profile, args.region)
    get_secret(client, args.name)
