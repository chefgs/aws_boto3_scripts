"""Create a secret in AWS Secrets Manager."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_secret(client, name, secret_string):
    """Create a secret and return the secret ARN."""
    try:
        response = client.create_secret(Name=name, SecretString=secret_string)
        arn = response["ARN"]
        logger.info("Created secret: %s", name)
        return arn
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create secret %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create a Secrets Manager secret")
    parser.add_argument("--name", required=True, help="Secret name")
    parser.add_argument("--secret-string", required=True, help="Secret value")
    args = parser.parse_args()
    client = get_client("secretsmanager", args.profile, args.region)
    create_secret(client, args.name, args.secret_string)
