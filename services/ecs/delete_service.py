"""Delete an ECS service."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_service(client, cluster, service_name, dry_run=False):
    """Delete an ECS service (drains tasks to 0 before deletion).

    Parameters
    ----------
    client       : boto3 ECS client
    cluster      : cluster name or ARN
    service_name : service name or ARN
    dry_run      : if True, log the action without making changes

    Returns
    -------
    dict  — the deleted service object, or None on dry_run
    """
    if dry_run:
        logger.info(
            "[DRY-RUN] Would delete service %s from cluster %s", service_name, cluster
        )
        return None
    try:
        # Drain tasks before deletion
        client.update_service(
            cluster=cluster, service=service_name, desiredCount=0
        )
        response = client.delete_service(cluster=cluster, service=service_name)
        service = response["service"]
        logger.info(
            "Deleted ECS service: %s from cluster %s (status: %s)",
            service_name,
            cluster,
            service.get("status"),
        )
        return service
    except botocore.exceptions.ClientError as exc:
        logger.error(
            "Failed to delete service %s from cluster %s: %s",
            service_name,
            cluster,
            exc,
        )
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete an ECS service")
    parser.add_argument("--cluster", required=True, help="Cluster name or ARN")
    parser.add_argument("--service-name", required=True, help="Service name or ARN")
    args = parser.parse_args()
    client = get_client("ecs", args.profile, args.region)
    delete_service(client, args.cluster, args.service_name, dry_run=args.dry_run)
