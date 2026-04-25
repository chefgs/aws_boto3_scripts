"""Put custom metric data to CloudWatch."""
import logging
from datetime import datetime, timezone

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def put_metric_data(client, namespace, metric_name, value, unit="None"):
    """Publish a single data point to CloudWatch Metrics."""
    try:
        response = client.put_metric_data(
            Namespace=namespace,
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Timestamp": datetime.now(tz=timezone.utc),
                    "Value": float(value),
                    "Unit": unit,
                }
            ],
        )
        logger.info("Published metric %s/%s = %s %s", namespace, metric_name, value, unit)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to put metric data: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Put custom metric data to CloudWatch")
    parser.add_argument("--namespace", required=True, help="Metric namespace")
    parser.add_argument("--metric-name", required=True, help="Metric name")
    parser.add_argument("--value", type=float, required=True, help="Metric value")
    parser.add_argument("--unit", default="None", help="Unit (e.g. Count, Seconds, Bytes)")
    args = parser.parse_args()
    client = get_client("cloudwatch", args.profile, args.region)
    put_metric_data(client, args.namespace, args.metric_name, args.value, args.unit)
