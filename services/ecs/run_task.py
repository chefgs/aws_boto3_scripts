"""Run a one-off ECS task."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def run_task(
    client,
    cluster,
    task_definition,
    launch_type="FARGATE",
    network_config=None,
    count=1,
):
    """Run one or more ECS tasks and return the list of task dicts.

    Parameters
    ----------
    client          : boto3 ECS client
    cluster         : cluster name or ARN
    task_definition : task definition ARN or 'family:revision'
    launch_type     : 'FARGATE' or 'EC2' (default: 'FARGATE')
    network_config  : optional awsvpcConfiguration dict
                      e.g. {'awsvpcConfiguration': {'subnets': [...], 'assignPublicIp': 'ENABLED'}}
    count           : number of task instances to start (default: 1)

    Returns
    -------
    list of dict  — task objects from the RunTask response
    """
    try:
        kwargs = {
            "cluster": cluster,
            "taskDefinition": task_definition,
            "launchType": launch_type,
            "count": count,
        }
        if network_config:
            kwargs["networkConfiguration"] = network_config
        response = client.run_task(**kwargs)
        tasks = response.get("tasks", [])
        for task in tasks:
            logger.info(
                "Started ECS task: %s (status: %s)",
                task.get("taskArn"),
                task.get("lastStatus"),
            )
        failures = response.get("failures", [])
        if failures:
            logger.warning("Run task failures: %s", failures)
        return tasks
    except botocore.exceptions.ClientError as exc:
        logger.error(
            "Failed to run task %s in cluster %s: %s", task_definition, cluster, exc
        )
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Run an ECS task")
    parser.add_argument("--cluster", required=True, help="Cluster name or ARN")
    parser.add_argument(
        "--task-definition", required=True, help="Task definition ARN or family:revision"
    )
    parser.add_argument(
        "--launch-type",
        default="FARGATE",
        choices=["FARGATE", "EC2"],
        help="Launch type (default: FARGATE)",
    )
    parser.add_argument(
        "--count", type=int, default=1, help="Number of task instances (default: 1)"
    )
    args = parser.parse_args()
    client = get_client("ecs", args.profile, args.region)
    run_task(client, args.cluster, args.task_definition, launch_type=args.launch_type, count=args.count)
