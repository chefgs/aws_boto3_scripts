"""Create a user in a Cognito user pool."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_user(client, pool_id, username, email=None):
    """Create a Cognito user and return the user data."""
    try:
        user_attrs = []
        if email:
            user_attrs.append({"Name": "email", "Value": email})
        response = client.admin_create_user(
            UserPoolId=pool_id,
            Username=username,
            UserAttributes=user_attrs,
        )
        user = response["User"]
        logger.info("Created user: %s in pool %s", username, pool_id)
        return user
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create user %s: %s", username, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create a Cognito user")
    parser.add_argument("--pool-id", required=True, help="User pool ID")
    parser.add_argument("--username", required=True, help="Username")
    parser.add_argument("--email", default=None, help="User email address")
    args = parser.parse_args()
    client = get_client("cognito-idp", args.profile, args.region)
    create_user(client, args.pool_id, args.username, args.email)
