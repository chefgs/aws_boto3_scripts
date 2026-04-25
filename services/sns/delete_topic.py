"""Delete an SNS topic."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_topic(client, topic_arn, dry_run=False):
    """Delete the specified SNS topic."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete topic: %s", topic_arn)
        return None
    try:
        response = client.delete_topic(TopicArn=topic_arn)
        logger.info("Deleted SNS topic: %s", topic_arn)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete topic %s: %s", topic_arn, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete an SNS topic")
    parser.add_argument("--topic-arn", required=True, help="SNS topic ARN")
    args = parser.parse_args()
    client = get_client("sns", args.profile, args.region)
    delete_topic(client, args.topic_arn, args.dry_run)
