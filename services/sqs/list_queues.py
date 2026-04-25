"""List SQS queues."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_queues(client):
    """Return a list of SQS queue URLs."""
    try:
        urls = []
        response = client.list_queues()
        urls = response.get("QueueUrls", [])
        for url in urls:
            logger.info("Queue: %s", url)
        return urls
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list queues: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List SQS queues")
    args = parser.parse_args()
    client = get_client("sqs", args.profile, args.region)
    list_queues(client)
