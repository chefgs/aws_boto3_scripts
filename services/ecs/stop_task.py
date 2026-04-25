"""Stop a running ECS task."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def stop_task(client, cluster, task_arn, reason="Stopped by boto3 script", dry_run=False):
    """Stop a running ECS task.

    Parameters
    ----------
    client    : boto3 ECS client
    cluster   : cluster name or ARN
    task_arn  : task ARN to stop
    reason    : human-readable stop reason (default: 'Stopped by boto3 script')
    dry_run   : if True, log the action without making changes

    Returns
    -------
    dict  — the stopped task object, or None on dry_run
    """
    if dry_run:
        logger.info("[DRY-RUN] Would stop task %s in cluster %s", task_arn, cluster)
        return None
    try:
        response = client.stop_task(cluster=cluster, task=task_arn, reason=reason)
        task = response["task"]
        logger.info(
            "Stopped ECS task: %s (status: %s)", task_arn, task.get("lastStatus")
        )
        return task
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to stop task %s in cluster %s: %s", task_arn, cluster, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Stop an ECS task")
    parser.add_argument("--cluster", required=True, help="Cluster name or ARN")
    parser.add_argument("--task", required=True, help="Task ARN to stop")
    parser.add_argument(
        "--reason",
        default="Stopped by boto3 script",
        help="Stop reason",
    )
    args = parser.parse_args()
    client = get_client("ecs", args.profile, args.region)
    stop_task(client, args.cluster, args.task, reason=args.reason, dry_run=args.dry_run)
