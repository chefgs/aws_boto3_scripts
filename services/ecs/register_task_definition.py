"""Register an ECS task definition."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def register_task_definition(
    client,
    family,
    container_name,
    image,
    cpu="256",
    memory="512",
    network_mode="awsvpc",
):
    """Register an ECS task definition and return the task definition dict.

    Parameters
    ----------
    client         : boto3 ECS client
    family         : task definition family name
    container_name : name of the container
    image          : container image URI
    cpu            : CPU units as string (e.g. '256')
    memory         : memory in MiB as string (e.g. '512')
    network_mode   : network mode ('awsvpc', 'bridge', 'host', 'none')

    Returns
    -------
    dict  — the registered taskDefinition object
    """
    try:
        response = client.register_task_definition(
            family=family,
            networkMode=network_mode,
            containerDefinitions=[
                {
                    "name": container_name,
                    "image": image,
                    "cpu": int(cpu),
                    "memory": int(memory),
                    "essential": True,
                }
            ],
            cpu=cpu,
            memory=memory,
        )
        task_def = response["taskDefinition"]
        arn = task_def["taskDefinitionArn"]
        logger.info(
            "Registered task definition: %s (revision %s) — %s",
            family,
            task_def["revision"],
            arn,
        )
        return task_def
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to register task definition %s: %s", family, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Register an ECS task definition")
    parser.add_argument("--family", required=True, help="Task definition family name")
    parser.add_argument("--container-name", required=True, help="Container name")
    parser.add_argument("--image", required=True, help="Container image URI")
    parser.add_argument("--cpu", default="256", help="CPU units (default: 256)")
    parser.add_argument("--memory", default="512", help="Memory in MiB (default: 512)")
    parser.add_argument(
        "--network-mode", default="awsvpc", help="Network mode (default: awsvpc)"
    )
    args = parser.parse_args()
    client = get_client("ecs", args.profile, args.region)
    register_task_definition(
        client,
        args.family,
        args.container_name,
        args.image,
        cpu=args.cpu,
        memory=args.memory,
        network_mode=args.network_mode,
    )
