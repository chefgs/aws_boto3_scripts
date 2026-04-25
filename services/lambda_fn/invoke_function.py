"""Invoke a Lambda function."""
import json
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def invoke_function(client, function_name, payload=None):
    """Invoke a Lambda function synchronously and return the response."""
    try:
        kwargs = {"FunctionName": function_name, "InvocationType": "RequestResponse"}
        if payload:
            kwargs["Payload"] = json.dumps(payload).encode()
        response = client.invoke(**kwargs)
        status_code = response["StatusCode"]
        body = response["Payload"].read().decode()
        logger.info("Invoked %s | status=%s | response=%s", function_name, status_code, body)
        return {"StatusCode": status_code, "Body": body}
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to invoke function %s: %s", function_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Invoke a Lambda function")
    parser.add_argument("--function-name", required=True, help="Function name")
    parser.add_argument("--payload", default=None, help="JSON payload string")
    args = parser.parse_args()
    payload = json.loads(args.payload) if args.payload else None
    client = get_client("lambda", args.profile, args.region)
    invoke_function(client, args.function_name, payload)
