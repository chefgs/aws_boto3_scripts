"""Create a CloudWatch alarm."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_alarm(client, alarm_name, metric, namespace, threshold, comparison="GreaterThanThreshold", period=300, evaluation_periods=1):
    """Create a CloudWatch alarm and return the response."""
    try:
        response = client.put_metric_alarm(
            AlarmName=alarm_name,
            MetricName=metric,
            Namespace=namespace,
            Statistic="Average",
            Period=period,
            EvaluationPeriods=evaluation_periods,
            Threshold=float(threshold),
            ComparisonOperator=comparison,
        )
        logger.info("Created/updated alarm: %s", alarm_name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create alarm %s: %s", alarm_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create a CloudWatch alarm")
    parser.add_argument("--alarm-name", required=True, help="Alarm name")
    parser.add_argument("--metric", required=True, help="Metric name")
    parser.add_argument("--namespace", required=True, help="Metric namespace")
    parser.add_argument("--threshold", type=float, required=True, help="Alarm threshold")
    parser.add_argument(
        "--comparison",
        default="GreaterThanThreshold",
        help="Comparison operator",
    )
    args = parser.parse_args()
    client = get_client("cloudwatch", args.profile, args.region)
    create_alarm(client, args.alarm_name, args.metric, args.namespace, args.threshold, args.comparison)
