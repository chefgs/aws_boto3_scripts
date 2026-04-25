"""Create a VPC with subnet, internet gateway, and route table."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_vpc(client, cidr="10.0.0.0/16"):
    """Create a VPC with one public subnet, IGW, and a route table.

    Returns a dict with keys: vpc_id, subnet_id, igw_id, route_table_id.
    """
    try:
        vpc_resp = client.create_vpc(CidrBlock=cidr)
        vpc_id = vpc_resp["Vpc"]["VpcId"]
        logger.info("Created VPC: %s", vpc_id)

        subnet_resp = client.create_subnet(VpcId=vpc_id, CidrBlock="10.0.1.0/24")
        subnet_id = subnet_resp["Subnet"]["SubnetId"]
        logger.info("Created subnet: %s", subnet_id)

        igw_resp = client.create_internet_gateway()
        igw_id = igw_resp["InternetGateway"]["InternetGatewayId"]
        client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        logger.info("Created and attached IGW: %s", igw_id)

        rt_resp = client.create_route_table(VpcId=vpc_id)
        rt_id = rt_resp["RouteTable"]["RouteTableId"]
        client.create_route(
            RouteTableId=rt_id,
            DestinationCidrBlock="0.0.0.0/0",
            GatewayId=igw_id,
        )
        client.associate_route_table(RouteTableId=rt_id, SubnetId=subnet_id)
        logger.info("Created route table: %s", rt_id)

        return {
            "vpc_id": vpc_id,
            "subnet_id": subnet_id,
            "igw_id": igw_id,
            "route_table_id": rt_id,
        }
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create VPC: %s", exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create a VPC with subnet, IGW, and route table")
    parser.add_argument("--cidr", default="10.0.0.0/16", help="VPC CIDR block")
    args = parser.parse_args()
    client = get_client("ec2", args.profile, args.region)
    create_vpc(client, args.cidr)
