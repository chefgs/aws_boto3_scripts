"""List users in a Cognito user pool."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_users(client, pool_id):
    """Return a list of Cognito user dicts for the given pool."""
    try:
        users = []
        response = client.list_users(UserPoolId=pool_id)
        users.extend(response.get("Users", []))
        for user in users:
            logger.info("User: %s | status=%s", user["Username"], user["UserStatus"])
        return users
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list users in pool %s: %s", pool_id, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List Cognito users")
    parser.add_argument("--pool-id", required=True, help="User pool ID")
    args = parser.parse_args()
    client = get_client("cognito-idp", args.profile, args.region)
    list_users(client, args.pool_id)
