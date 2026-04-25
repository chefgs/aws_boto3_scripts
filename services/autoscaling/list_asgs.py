"""List Auto Scaling groups."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_asgs(client):
    """Return a list of Auto Scaling group dicts."""
    try:
        paginator = client.get_paginator("describe_auto_scaling_groups")
        asgs = []
        for page in paginator.paginate():
            asgs.extend(page.get("AutoScalingGroups", []))
        for asg in asgs:
            logger.info(
                "ASG: %s | min=%s max=%s desired=%s",
                asg["AutoScalingGroupName"],
                asg["MinSize"],
                asg["MaxSize"],
                asg["DesiredCapacity"],
            )
        return asgs
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list ASGs: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List Auto Scaling groups")
    args = parser.parse_args()
    client = get_client("autoscaling", args.profile, args.region)
    list_asgs(client)
