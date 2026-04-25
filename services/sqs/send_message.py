"""Send a message to an SQS queue."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def send_message(client, queue_url, message):
    """Send a message to an SQS queue and return the message ID."""
    try:
        response = client.send_message(QueueUrl=queue_url, MessageBody=message)
        msg_id = response["MessageId"]
        logger.info("Sent message %s to %s", msg_id, queue_url)
        return msg_id
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to send message: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Send a message to an SQS queue")
    parser.add_argument("--queue-url", required=True, help="Queue URL")
    parser.add_argument("--message", required=True, help="Message body")
    args = parser.parse_args()
    client = get_client("sqs", args.profile, args.region)
    send_message(client, args.queue_url, args.message)
