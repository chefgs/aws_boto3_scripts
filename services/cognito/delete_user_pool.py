"""Delete a Cognito user pool."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_user_pool(client, pool_id, dry_run=False):
    """Delete the specified Cognito user pool."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete user pool: %s", pool_id)
        return None
    try:
        response = client.delete_user_pool(UserPoolId=pool_id)
        logger.info("Deleted user pool: %s", pool_id)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete user pool %s: %s", pool_id, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete a Cognito user pool")
    parser.add_argument("--pool-id", required=True, help="User pool ID")
    args = parser.parse_args()
    client = get_client("cognito-idp", args.profile, args.region)
    delete_user_pool(client, args.pool_id, args.dry_run)
