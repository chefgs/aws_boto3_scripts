"""Create an SQS queue."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_queue(client, name, fifo=False):
    """Create an SQS queue and return the queue URL."""
    try:
        queue_name = name + ".fifo" if fifo and not name.endswith(".fifo") else name
        attrs = {}
        if fifo:
            attrs["FifoQueue"] = "true"
        response = client.create_queue(QueueName=queue_name, Attributes=attrs)
        url = response["QueueUrl"]
        logger.info("Created SQS queue: %s", url)
        return url
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create queue %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create an SQS queue")
    parser.add_argument("--name", required=True, help="Queue name")
    parser.add_argument("--fifo", action="store_true", help="Create a FIFO queue")
    args = parser.parse_args()
    client = get_client("sqs", args.profile, args.region)
    create_queue(client, args.name, args.fifo)
