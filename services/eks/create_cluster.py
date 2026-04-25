"""Create an EKS cluster."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_cluster(
    client,
    name,
    role_arn,
    resources_vpc_config,
    kubernetes_version="1.29",
):
    """Create an EKS cluster and return the cluster dict.

    Parameters
    ----------
    client                : boto3 EKS client
    name                  : cluster name
    role_arn              : IAM role ARN that EKS uses to manage AWS resources
    resources_vpc_config  : dict with at minimum 'subnetIds' key
                            e.g. {'subnetIds': ['subnet-abc'], 'endpointPublicAccess': True}
    kubernetes_version    : Kubernetes version string (default: '1.29')

    Returns
    -------
    dict  — the cluster object from the CreateCluster response
    """
    try:
        response = client.create_cluster(
            name=name,
            version=kubernetes_version,
            roleArn=role_arn,
            resourcesVpcConfig=resources_vpc_config,
        )
        cluster = response["cluster"]
        arn = cluster["arn"]
        logger.info(
            "Created EKS cluster: %s (version %s) — %s",
            name,
            kubernetes_version,
            arn,
        )
        return cluster
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create EKS cluster %s: %s", name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create an EKS cluster")
    parser.add_argument("--name", required=True, help="Cluster name")
    parser.add_argument("--role-arn", required=True, help="IAM role ARN for EKS")
    parser.add_argument(
        "--subnet-ids",
        required=True,
        nargs="+",
        help="One or more VPC subnet IDs",
    )
    parser.add_argument(
        "--kubernetes-version", default="1.29", help="Kubernetes version (default: 1.29)"
    )
    args = parser.parse_args()
    client = get_client("eks", args.profile, args.region)
    create_cluster(
        client,
        args.name,
        args.role_arn,
        {"subnetIds": args.subnet_ids},
        kubernetes_version=args.kubernetes_version,
    )
