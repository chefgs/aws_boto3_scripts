"""Create a Lambda function from an in-memory zip."""
import io
import logging
import zipfile

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)

_DEFAULT_HANDLER_CODE = b"""
def handler(event, context):
    return {'statusCode': 200, 'body': 'Hello from Lambda!'}
"""


def _make_zip(handler_code=_DEFAULT_HANDLER_CODE):
    """Return a zip file bytes object containing lambda_function.py."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("lambda_function.py", handler_code)
    return buf.getvalue()


def create_function(client, function_name, runtime, role_arn, handler="lambda_function.handler"):
    """Create a Lambda function and return the function ARN."""
    try:
        response = client.create_function(
            FunctionName=function_name,
            Runtime=runtime,
            Role=role_arn,
            Handler=handler,
            Code={"ZipFile": _make_zip()},
            Description=f"Created by boto3-scripts",
        )
        arn = response["FunctionArn"]
        logger.info("Created Lambda function: %s (%s)", function_name, arn)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create function %s: %s", function_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create a Lambda function")
    parser.add_argument("--function-name", required=True, help="Function name")
    parser.add_argument("--runtime", default="python3.11", help="Runtime")
    parser.add_argument("--role-arn", required=True, help="Execution role ARN")
    parser.add_argument("--handler", default="lambda_function.handler", help="Handler")
    args = parser.parse_args()
    client = get_client("lambda", args.profile, args.region)
    create_function(client, args.function_name, args.runtime, args.role_arn, args.handler)
