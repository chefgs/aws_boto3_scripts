"""Create one or more ECS clusters."""
import logging
import random

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_cluster(client, cluster_name):
    """Create an ECS cluster and return the response."""
    try:
        response = client.create_cluster(clusterName=cluster_name)
        arn = response["cluster"]["clusterArn"]
        logger.info("Created ECS cluster: %s (%s)", cluster_name, arn)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create cluster %s: %s", cluster_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create ECS cluster(s)")
    parser.add_argument("--prefix", default="boto3cluster", help="Cluster name prefix")
    parser.add_argument("--count", type=int, default=1, help="Number of clusters")
    args = parser.parse_args()
    client = get_client("ecs", args.profile, args.region)
    for _ in range(args.count):
        name = args.prefix + str(random.randint(0, 99999))
        create_cluster(client, name)
