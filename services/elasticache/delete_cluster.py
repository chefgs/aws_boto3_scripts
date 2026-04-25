"""Delete an ElastiCache cluster."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_cluster(client, cluster_id, dry_run=False):
    """Delete the specified ElastiCache cluster."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete ElastiCache cluster: %s", cluster_id)
        return None
    try:
        response = client.delete_cache_cluster(CacheClusterId=cluster_id)
        status = response["CacheCluster"]["CacheClusterStatus"]
        logger.info("Cluster %s is now: %s", cluster_id, status)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete cluster %s: %s", cluster_id, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete an ElastiCache cluster")
    parser.add_argument("--cluster-id", required=True, help="Cluster identifier")
    args = parser.parse_args()
    client = get_client("elasticache", args.profile, args.region)
    delete_cluster(client, args.cluster_id, args.dry_run)
