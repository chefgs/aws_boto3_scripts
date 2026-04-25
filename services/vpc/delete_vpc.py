"""Delete a VPC and its dependencies."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def delete_vpc(client, vpc_id, dry_run=False):
    """Delete a VPC after detaching/deleting its dependencies."""
    if dry_run:
        logger.info("[DRY-RUN] Would delete VPC: %s", vpc_id)
        return None
    try:
        # Detach and delete internet gateways
        igws = client.describe_internet_gateways(
            Filters=[{"Name": "attachment.vpc-id", "Values": [vpc_id]}]
        ).get("InternetGateways", [])
        for igw in igws:
            igw_id = igw["InternetGatewayId"]
            client.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
            client.delete_internet_gateway(InternetGatewayId=igw_id)
            logger.info("Deleted IGW: %s", igw_id)

        # Delete subnets
        subnets = client.describe_subnets(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        ).get("Subnets", [])
        for subnet in subnets:
            client.delete_subnet(SubnetId=subnet["SubnetId"])
            logger.info("Deleted subnet: %s", subnet["SubnetId"])

        # Delete non-main route tables
        rts = client.describe_route_tables(
            Filters=[{"Name": "vpc-id", "Values": [vpc_id]}]
        ).get("RouteTables", [])
        for rt in rts:
            if not any(a.get("Main") for a in rt.get("Associations", [])):
                client.delete_route_table(RouteTableId=rt["RouteTableId"])
                logger.info("Deleted route table: %s", rt["RouteTableId"])

        client.delete_vpc(VpcId=vpc_id)
        logger.info("Deleted VPC: %s", vpc_id)
        return {"deleted_vpc": vpc_id}
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to delete VPC %s: %s", vpc_id, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Delete a VPC and its dependencies")
    parser.add_argument("--vpc-id", required=True, help="VPC ID")
    args = parser.parse_args()
    client = get_client("ec2", args.profile, args.region)
    delete_vpc(client, args.vpc_id, args.dry_run)
