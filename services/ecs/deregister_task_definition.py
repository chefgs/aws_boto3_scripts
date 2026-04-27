"""Deregister an ECS task definition."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def deregister_task_definition(client, task_definition, dry_run=False):
    """Deregister an ECS task definition by ARN or family:revision.

    Parameters
    ----------
    client          : boto3 ECS client
    task_definition : task definition ARN or 'family:revision' string
    dry_run         : if True, log the action without making changes

    Returns
    -------
    dict  — the deregistered taskDefinition object, or None on dry_run
    """
    if dry_run:
        logger.info("[DRY-RUN] Would deregister task definition: %s", task_definition)
        return None
    try:
        response = client.deregister_task_definition(taskDefinition=task_definition)
        task_def = response["taskDefinition"]
        logger.info(
            "Deregistered task definition: %s (status: %s)",
            task_definition,
            task_def.get("status"),
        )
        return task_def
    except botocore.exceptions.ClientError as exc:
        logger.error(
            "Failed to deregister task definition %s: %s", task_definition, exc
        )
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Deregister an ECS task definition")
    parser.add_argument(
        "--task-definition",
        required=True,
        help="Task definition ARN or family:revision",
    )
    args = parser.parse_args()
    client = get_client("ecs", args.profile, args.region)
    deregister_task_definition(client, args.task_definition, dry_run=args.dry_run)
