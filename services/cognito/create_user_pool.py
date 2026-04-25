"""Create a Cognito user pool."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_user_pool(client, pool_name):
    """Create a Cognito user pool and return the pool ID."""
    try:
        response = client.create_user_pool(PoolName=pool_name)
        pool_id = response["UserPool"]["Id"]
        logger.info("Created user pool: %s (%s)", pool_name, pool_id)
        return pool_id
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create user pool %s: %s", pool_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create a Cognito user pool")
    parser.add_argument("--pool-name", required=True, help="User pool name")
    args = parser.parse_args()
    client = get_client("cognito-idp", args.profile, args.region)
    create_user_pool(client, args.pool_name)
