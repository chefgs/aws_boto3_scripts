"""Create a CloudFormation stack."""
import json
import logging

import botocore.exceptions

from utils.args import base_parser
from utils.logging_helper import setup_logging
from utils.session import get_client

logger = logging.getLogger(__name__)


def create_stack(client, stack_name, template_body=None, template_url=None, parameters=None):
    """Create a CloudFormation stack and return the stack ID."""
    try:
        kwargs = {"StackName": stack_name}
        if template_body:
            kwargs["TemplateBody"] = template_body
        elif template_url:
            kwargs["TemplateURL"] = template_url
        if parameters:
            kwargs["Parameters"] = parameters
        response = client.create_stack(**kwargs)
        stack_id = response["StackId"]
        logger.info("Creating stack: %s (%s)", stack_name, stack_id)
        return stack_id
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create stack %s: %s", stack_name, exc)
        raise


if __name__ == "__main__":
    setup_logging()
    parser = base_parser("Create a CloudFormation stack")
    parser.add_argument("--stack-name", required=True, help="Stack name")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--template-file", help="Local template file path")
    group.add_argument("--template-url", help="S3 URL to template")
    parser.add_argument(
        "--parameters",
        default=None,
        help='Parameters as JSON, e.g. \'[{"ParameterKey":"K","ParameterValue":"V"}]\'',
    )
    args = parser.parse_args()
    client = get_client("cloudformation", args.profile, args.region)
    template_body = None
    if args.template_file:
        with open(args.template_file) as f:
            template_body = f.read()
    params = json.loads(args.parameters) if args.parameters else None
    create_stack(client, args.stack_name, template_body, args.template_url, params)
