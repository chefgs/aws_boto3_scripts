"""List SNS topics."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_topics(client):
    """Return a list of SNS topic ARNs."""
    try:
        paginator = client.get_paginator("list_topics")
        topics = []
        for page in paginator.paginate():
            topics.extend([t["TopicArn"] for t in page.get("Topics", [])])
        for arn in topics:
            logger.info("Topic: %s", arn)
        return topics
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list topics: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List SNS topics")
    args = parser.parse_args()
    client = get_client("sns", args.profile, args.region)
    list_topics(client)
