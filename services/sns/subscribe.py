"""Subscribe an endpoint to an SNS topic."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def subscribe(client, topic_arn, protocol, endpoint):
    """Subscribe an endpoint to an SNS topic and return the subscription ARN."""
    try:
        response = client.subscribe(
            TopicArn=topic_arn, Protocol=protocol, Endpoint=endpoint
        )
        sub_arn = response.get("SubscriptionArn", "pending")
        logger.info("Subscribed %s to %s (ARN: %s)", endpoint, topic_arn, sub_arn)
        return sub_arn
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to subscribe %s: %s", endpoint, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Subscribe to an SNS topic")
    parser.add_argument("--topic-arn", required=True, help="SNS topic ARN")
    parser.add_argument("--protocol", required=True, help="Protocol (email, sqs, lambda, …)")
    parser.add_argument("--endpoint", required=True, help="Endpoint (email address, ARN, …)")
    args = parser.parse_args()
    client = get_client("sns", args.profile, args.region)
    subscribe(client, args.topic_arn, args.protocol, args.endpoint)
