"""List ECS tasks in a cluster."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_tasks(client, cluster, service_name=None, desired_status="RUNNING"):
    """Return a list of ECS task ARNs in the given cluster.

    Parameters
    ----------
    client         : boto3 ECS client
    cluster        : cluster name or ARN
    service_name   : optional service name to filter tasks
    desired_status : 'RUNNING', 'PENDING', or 'STOPPED' (default: 'RUNNING')

    Returns
    -------
    list of str  — task ARNs
    """
    try:
        kwargs = {"cluster": cluster, "desiredStatus": desired_status}
        if service_name:
            kwargs["serviceName"] = service_name
        paginator = client.get_paginator("list_tasks")
        arns = []
        for page in paginator.paginate(**kwargs):
            arns.extend(page.get("taskArns", []))
        for arn in arns:
            logger.info("Task: %s", arn)
        return arns
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list tasks in cluster %s: %s", cluster, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List ECS tasks")
    parser.add_argument("--cluster", required=True, help="Cluster name or ARN")
    parser.add_argument("--service-name", default=None, help="Filter by service name")
    parser.add_argument(
        "--desired-status",
        default="RUNNING",
        choices=["RUNNING", "PENDING", "STOPPED"],
        help="Filter by desired status (default: RUNNING)",
    )
    args = parser.parse_args()
    client = get_client("ecs", args.profile, args.region)
    list_tasks(
        client,
        args.cluster,
        service_name=args.service_name,
        desired_status=args.desired_status,
    )
