"""List CloudFormation stacks."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_stacks(client, status_filter=None):
    """Return a list of CloudFormation stack summaries."""
    try:
        kwargs = {}
        if status_filter:
            kwargs["StackStatusFilter"] = status_filter if isinstance(status_filter, list) else [status_filter]
        paginator = client.get_paginator("list_stacks")
        stacks = []
        for page in paginator.paginate(**kwargs):
            stacks.extend(page.get("StackSummaries", []))
        for stack in stacks:
            logger.info("Stack: %s | status=%s", stack["StackName"], stack["StackStatus"])
        return stacks
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list stacks: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List CloudFormation stacks")
    parser.add_argument("--status-filter", default=None, help="Stack status filter")
    args = parser.parse_args()
    client = get_client("cloudformation", args.profile, args.region)
    list_stacks(client, args.status_filter)
