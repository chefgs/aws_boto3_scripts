"""Terminate an EC2 instance."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_instance(client, instance_id, dry_run=False):
    """Terminate the specified EC2 instance."""
    if dry_run:
        logger.info("[DRY-RUN] Would terminate instance: %s", instance_id)
        return None
    try:
        response = client.terminate_instances(InstanceIds=[instance_id])
        state = response["TerminatingInstances"][0]["CurrentState"]["Name"]
        logger.info("Instance %s is now: %s", instance_id, state)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to terminate instance %s: %s", instance_id, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Terminate an EC2 instance")
    parser.add_argument("--instance-id", required=True, help="EC2 instance ID")
    args = parser.parse_args()
    client = get_client("ec2", args.profile, args.region)
    delete_instance(client, args.instance_id, args.dry_run)
