"""Receive messages from an SQS queue."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def receive_messages(client, queue_url, max_count=10):
    """Receive up to max_count messages from an SQS queue."""
    try:
        response = client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=min(max_count, 10),
        )
        messages = response.get("Messages", [])
        for msg in messages:
            logger.info("Received message %s: %s", msg["MessageId"], msg["Body"])
        return messages
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to receive messages: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Receive messages from an SQS queue")
    parser.add_argument("--queue-url", required=True, help="Queue URL")
    parser.add_argument("--max-count", type=int, default=10, help="Max messages (1-10)")
    args = parser.parse_args()
    client = get_client("sqs", args.profile, args.region)
    receive_messages(client, args.queue_url, args.max_count)
