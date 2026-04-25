"""Describe a single EC2 instance."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def describe_instance(client, instance_id):
    """Return details for a single EC2 instance."""
    try:
        response = client.describe_instances(InstanceIds=[instance_id])
        reservations = response.get("Reservations", [])
        if not reservations:
            logger.warning("No instance found with ID: %s", instance_id)
            return None
        inst = reservations[0]["Instances"][0]
        logger.info("Instance %s: %s", instance_id, inst)
        return inst
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to describe instance %s: %s", instance_id, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Describe an EC2 instance")
    parser.add_argument("--instance-id", required=True, help="EC2 instance ID")
    args = parser.parse_args()
    client = get_client("ec2", args.profile, args.region)
    describe_instance(client, args.instance_id)
