"""Delete an IAM user."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_user(client, username, dry_run=False):
    """Delete the specified IAM user."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete user: %s", username)
        return None
    try:
        response = client.delete_user(UserName=username)
        logger.info("Deleted IAM user: %s", username)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete user %s: %s", username, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete an IAM user")
    parser.add_argument("--username", required=True, help="IAM username")
    args = parser.parse_args()
    client = get_client("iam", args.profile, args.region)
    delete_user(client, args.username, args.dry_run)
