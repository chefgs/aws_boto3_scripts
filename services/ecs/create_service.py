"""Create an ECS service within a cluster."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_service(
    client,
    cluster,
    service_name,
    task_definition,
    desired_count=1,
    launch_type="FARGATE",
):
    """Create an ECS service and return the service dict.

    Parameters
    ----------
    client          : boto3 ECS client
    cluster         : cluster name or ARN
    service_name    : name for the new service
    task_definition : task definition ARN or 'family:revision'
    desired_count   : number of desired tasks (default: 1)
    launch_type     : 'FARGATE' or 'EC2' (default: 'FARGATE')

    Returns
    -------
    dict  — the created service object
    """
    try:
        response = client.create_service(
            cluster=cluster,
            serviceName=service_name,
            taskDefinition=task_definition,
            desiredCount=desired_count,
            launchType=launch_type,
        )
        service = response["service"]
        arn = service["serviceArn"]
        logger.info(
            "Created ECS service: %s in cluster %s (%s)", service_name, cluster, arn
        )
        return service
    except botocore.exceptions.ClientError as exc:
        logger.error(
            "Failed to create service %s in cluster %s: %s", service_name, cluster, exc
        )
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create an ECS service")
    parser.add_argument("--cluster", required=True, help="Cluster name or ARN")
    parser.add_argument("--service-name", required=True, help="Service name")
    parser.add_argument(
        "--task-definition", required=True, help="Task definition ARN or family:revision"
    )
    parser.add_argument(
        "--desired-count", type=int, default=1, help="Desired task count (default: 1)"
    )
    parser.add_argument(
        "--launch-type",
        default="FARGATE",
        choices=["FARGATE", "EC2"],
        help="Launch type (default: FARGATE)",
    )
    args = parser.parse_args()
    client = get_client("ecs", args.profile, args.region)
    create_service(
        client,
        args.cluster,
        args.service_name,
        args.task_definition,
        desired_count=args.desired_count,
        launch_type=args.launch_type,
    )
