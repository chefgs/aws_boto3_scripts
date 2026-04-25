"""List ECS clusters."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_clusters(client):
    """Return a list of ECS cluster ARNs."""
    try:
        paginator = client.get_paginator("list_clusters")
        arns = []
        for page in paginator.paginate():
            arns.extend(page.get("clusterArns", []))
        for arn in arns:
            logger.info("Cluster: %s", arn)
        return arns
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list clusters: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List ECS clusters")
    args = parser.parse_args()
    client = get_client("ecs", args.profile, args.region)
    list_clusters(client)
