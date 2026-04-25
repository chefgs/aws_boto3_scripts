"""List CloudWatch alarms."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_alarms(client):
    """Return a list of CloudWatch alarm dicts."""
    try:
        paginator = client.get_paginator("describe_alarms")
        alarms = []
        for page in paginator.paginate():
            alarms.extend(page.get("MetricAlarms", []))
        for alarm in alarms:
            logger.info("Alarm: %s | state=%s", alarm["AlarmName"], alarm["StateValue"])
        return alarms
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list alarms: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List CloudWatch alarms")
    args = parser.parse_args()
    client = get_client("cloudwatch", args.profile, args.region)
    list_alarms(client)
