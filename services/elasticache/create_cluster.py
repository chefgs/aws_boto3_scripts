"""Create an ElastiCache cluster."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_cluster(client, cluster_id, engine="redis", node_type="cache.t3.micro", num_nodes=1):
    """Create an ElastiCache cluster and return the cluster data."""
    try:
        response = client.create_cache_cluster(
            CacheClusterId=cluster_id,
            Engine=engine,
            CacheNodeType=node_type,
            NumCacheNodes=num_nodes,
        )
        cluster = response["CacheCluster"]
        status = cluster["CacheClusterStatus"]
        logger.info("Created ElastiCache cluster: %s | engine=%s | status=%s", cluster_id, engine, status)
        return cluster
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create ElastiCache cluster %s: %s", cluster_id, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create an ElastiCache cluster")
    parser.add_argument("--cluster-id", required=True, help="Cluster identifier")
    parser.add_argument("--engine", default="redis", choices=["redis", "memcached"], help="Cache engine")
    parser.add_argument("--node-type", default="cache.t3.micro", help="Node type")
    parser.add_argument("--num-nodes", type=int, default=1, help="Number of cache nodes")
    args = parser.parse_args()
    client = get_client("elasticache", args.profile, args.region)
    create_cluster(client, args.cluster_id, args.engine, args.node_type, args.num_nodes)
