"""Delete a secret from AWS Secrets Manager."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_secret(client, name, dry_run=False):
    """Delete the specified secret (with recovery window)."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete secret: %s", name)
        return None
    try:
        response = client.delete_secret(
            SecretId=name, ForceDeleteWithoutRecovery=False
        )
        logger.info("Scheduled secret deletion: %s", name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete secret %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete a Secrets Manager secret")
    parser.add_argument("--name", required=True, help="Secret name or ARN")
    args = parser.parse_args()
    client = get_client("secretsmanager", args.profile, args.region)
    delete_secret(client, args.name, args.dry_run)
