"""Delete an SQS queue."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_queue(client, queue_url, dry_run=False):
    """Delete the specified SQS queue."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete queue: %s", queue_url)
        return None
    try:
        response = client.delete_queue(QueueUrl=queue_url)
        logger.info("Deleted SQS queue: %s", queue_url)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete queue %s: %s", queue_url, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete an SQS queue")
    parser.add_argument("--queue-url", required=True, help="Queue URL")
    args = parser.parse_args()
    client = get_client("sqs", args.profile, args.region)
    delete_queue(client, args.queue_url, args.dry_run)
