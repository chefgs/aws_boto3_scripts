"""Create an RDS DB instance."""
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_db_instance(client, db_id, engine, db_class, username, password, storage=20):
    """Create an RDS DB instance and return the DB instance data."""
    try:
        response = client.create_db_instance(
            DBInstanceIdentifier=db_id,
            Engine=engine,
            DBInstanceClass=db_class,
            MasterUsername=username,
            MasterUserPassword=password,
            AllocatedStorage=storage,
        )
        status = response["DBInstance"]["DBInstanceStatus"]
        logger.info("Created RDS instance %s | engine=%s | status=%s", db_id, engine, status)
        return response["DBInstance"]
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create DB instance %s: %s", db_id, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create an RDS DB instance")
    parser.add_argument("--db-id", required=True, help="DB instance identifier")
    parser.add_argument("--engine", default="mysql", help="Database engine")
    parser.add_argument("--db-class", default="db.t3.micro", help="DB instance class")
    parser.add_argument("--username", required=True, help="Master username")
    parser.add_argument("--password", required=True, help="Master password")
    parser.add_argument("--storage", type=int, default=20, help="Allocated storage (GB)")
    args = parser.parse_args()
    client = get_client("rds", args.profile, args.region)
    create_db_instance(
        client, args.db_id, args.engine, args.db_class,
        args.username, args.password, args.storage
    )
