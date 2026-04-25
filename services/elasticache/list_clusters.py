"""List ElastiCache clusters."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_clusters(client):
    """Return a list of ElastiCache cluster dicts."""
    try:
        paginator = client.get_paginator("describe_cache_clusters")
        clusters = []
        for page in paginator.paginate():
            clusters.extend(page.get("CacheClusters", []))
        for c in clusters:
            logger.info(
                "Cluster: %s | engine=%s | status=%s",
                c["CacheClusterId"],
                c.get("Engine"),
                c.get("CacheClusterStatus"),
            )
        return clusters
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list ElastiCache clusters: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List ElastiCache clusters")
    args = parser.parse_args()
    client = get_client("elasticache", args.profile, args.region)
    list_clusters(client)
