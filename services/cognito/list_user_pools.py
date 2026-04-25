"""List Cognito user pools."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_user_pools(client, max_results=60):
    """Return a list of Cognito user pool summaries."""
    try:
        pools = []
        response = client.list_user_pools(MaxResults=max_results)
        pools.extend(response.get("UserPools", []))
        for pool in pools:
            logger.info("Pool: %s (%s)", pool["Name"], pool["Id"])
        return pools
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list user pools: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List Cognito user pools")
    args = parser.parse_args()
    client = get_client("cognito-idp", args.profile, args.region)
    list_user_pools(client)
