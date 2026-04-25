"""Create an SNS topic."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_topic(client, name):
    """Create an SNS topic and return the topic ARN."""
    try:
        response = client.create_topic(Name=name)
        arn = response["TopicArn"]
        logger.info("Created SNS topic: %s (%s)", name, arn)
        return arn
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create topic %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create an SNS topic")
    parser.add_argument("--name", required=True, help="Topic name")
    args = parser.parse_args()
    client = get_client("sns", args.profile, args.region)
    create_topic(client, args.name)
