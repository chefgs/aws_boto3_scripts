"""Create an IAM user."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_user(client, username):
    """Create an IAM user and return the user data."""
    try:
        response = client.create_user(UserName=username)
        arn = response["User"]["Arn"]
        logger.info("Created IAM user: %s (%s)", username, arn)
        return response["User"]
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create user %s: %s", username, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create an IAM user")
    parser.add_argument("--username", required=True, help="IAM username")
    args = parser.parse_args()
    client = get_client("iam", args.profile, args.region)
    create_user(client, args.username)
