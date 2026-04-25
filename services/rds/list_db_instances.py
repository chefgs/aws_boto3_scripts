"""List RDS DB instances."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_db_instances(client):
    """Return a list of RDS DB instance dicts."""
    try:
        paginator = client.get_paginator("describe_db_instances")
        instances = []
        for page in paginator.paginate():
            instances.extend(page.get("DBInstances", []))
        for inst in instances:
            logger.info(
                "DB %s | engine=%s | status=%s",
                inst["DBInstanceIdentifier"],
                inst["Engine"],
                inst["DBInstanceStatus"],
            )
        return instances
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list DB instances: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List RDS DB instances")
    args = parser.parse_args()
    client = get_client("rds", args.profile, args.region)
    list_db_instances(client)
