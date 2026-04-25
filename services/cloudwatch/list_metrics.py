"""List CloudWatch metrics."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def list_metrics(client, namespace=None):
    """Return a list of CloudWatch metric dicts."""
    try:
        kwargs = {}
        if namespace:
            kwargs["Namespace"] = namespace
        paginator = client.get_paginator("list_metrics")
        metrics = []
        for page in paginator.paginate(**kwargs):
            metrics.extend(page.get("Metrics", []))
        for metric in metrics:
            logger.info("Metric: %s/%s", metric.get("Namespace"), metric.get("MetricName"))
        return metrics
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to list metrics: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("List CloudWatch metrics")
    parser.add_argument("--namespace", default=None, help="Filter by namespace")
    args = parser.parse_args()
    client = get_client("cloudwatch", args.profile, args.region)
    list_metrics(client, args.namespace)
