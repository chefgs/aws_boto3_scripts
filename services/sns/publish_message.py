"""Publish a message to an SNS topic."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def publish_message(client, topic_arn, message, subject=None):
    """Publish a message to an SNS topic and return the message ID."""
    try:
        kwargs = {"TopicArn": topic_arn, "Message": message}
        if subject:
            kwargs["Subject"] = subject
        response = client.publish(**kwargs)
        msg_id = response["MessageId"]
        logger.info("Published message %s to %s", msg_id, topic_arn)
        return msg_id
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to publish to %s: %s", topic_arn, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Publish a message to an SNS topic")
    parser.add_argument("--topic-arn", required=True, help="SNS topic ARN")
    parser.add_argument("--message", required=True, help="Message body")
    parser.add_argument("--subject", default=None, help="Message subject (email)")
    args = parser.parse_args()
    client = get_client("sns", args.profile, args.region)
    publish_message(client, args.topic_arn, args.message, args.subject)
