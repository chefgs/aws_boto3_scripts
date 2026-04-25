"""List EC2 instances, optionally filtered by state."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_instances(client, state=None):
    """Return a list of instance dicts, optionally filtered by state."""
    try:
        filters = []
        if state:
            filters.append({"Name": "instance-state-name", "Values": [state]})
        paginator = client.get_paginator("describe_instances")
        instances = []
        for page in paginator.paginate(Filters=filters):
            for reservation in page["Reservations"]:
                for inst in reservation["Instances"]:
                    instances.append(inst)
                    logger.info(
                        "Instance %s | type=%s | state=%s",
                        inst["InstanceId"],
                        inst["InstanceType"],
                        inst["State"]["Name"],
                    )
        return instances
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list instances: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List EC2 instances")
    parser.add_argument(
        "--state",
        default=None,
        help="Filter by state (running, stopped, …)",
    )
    args = parser.parse_args()
    client = get_client("ec2", args.profile, args.region)
    list_instances(client, args.state)
