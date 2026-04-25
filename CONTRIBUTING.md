# Contributing to aws_boto3_scripts

Thank you for considering contributing to this project! Contributions of all kinds are welcome — bug fixes, new service scripts, documentation improvements, and test coverage.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Report a Bug](#how-to-report-a-bug)
- [How to Request a Feature](#how-to-request-a-feature)
- [Development Setup](#development-setup)
- [Adding a New Service Script](#adding-a-new-service-script)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting a Pull Request](#submitting-a-pull-request)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating you agree to abide by its terms.

---

## How to Report a Bug

1. Search [existing issues](https://github.com/chefgs/aws_boto3_scripts/issues) to avoid duplicates.
2. Open a new issue using the **Bug Report** template.
3. Include:
   - Python version (`python --version`)
   - boto3/botocore version (`pip show boto3`)
   - The full command you ran
   - The full error output (stack trace)
   - Whether you were running against real AWS or using moto mocks

---

## How to Request a Feature

1. Search [existing issues](https://github.com/chefgs/aws_boto3_scripts/issues) and the [roadmap](ROADMAP.md).
2. Open a new issue using the **Feature Request** template.
3. Describe:
   - The AWS service and operation(s) you need
   - Why it's valuable
   - Any relevant AWS API documentation links

---

## Development Setup

```bash
# 1. Fork and clone
git clone https://github.com/<your-username>/aws_boto3_scripts.git
cd aws_boto3_scripts

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
make install
# or: pip install -r requirements.txt

# 4. Verify tests pass
make test
```

---

## Adding a New Service Script

Place scripts under `services/<service_name>/`. Follow this structure:

```python
"""Create a <resource> in <service>."""
import logging
import botocore.exceptions
from utils.session import get_client
from utils.args import base_parser
from utils.logging_helper import setup_logging

logger = logging.getLogger(__name__)


def create_resource(client, name, dry_run=False):
    """Create the resource. Returns the resource details or None on error."""
    if dry_run:
        logger.info("[DRY RUN] Would create resource: %s", name)
        return None
    try:
        response = client.create_something(Name=name)
        logger.info("Created resource: %s", name)
        return response
    except botocore.exceptions.ClientError as exc:
        logger.error("Failed to create resource: %s", exc)
        return None


def main():
    parser = base_parser(description="Create a <resource>")
    parser.add_argument("--name", required=True, help="Resource name")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating")
    args = parser.parse_args()
    setup_logging()
    client = get_client("<service>", profile=args.profile, region=args.region)
    create_resource(client, args.name, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
```

Checklist for new scripts:
- [ ] Imports from `utils.session`, `utils.args`, `utils.logging_helper`
- [ ] Exposes a callable function (testable without argparse)
- [ ] Wraps AWS calls in `try/except botocore.exceptions.ClientError`
- [ ] Adds `--dry-run` for any operation that creates, modifies, or deletes resources
- [ ] Has a corresponding test in `tests/test_<service>.py` using `@mock_aws`
- [ ] Has documentation in `docs/<service>.md`

---

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Maximum line length: 127 characters.
- Run lint before submitting:

```bash
make lint
```

---

## Testing

- Tests live in `tests/` and use [moto](https://github.com/getmoto/moto) to mock AWS.
- No real AWS credentials are required.
- Run the full suite:

```bash
make test
```

- Run a single test file:

```bash
pytest tests/test_s3.py -v
```

---

## Submitting a Pull Request

1. Create a branch from `main`: `git checkout -b feat/my-feature`
2. Make your changes.
3. Ensure `make lint` and `make test` both pass.
4. Push to your fork and open a pull request against `main`.
5. Fill in the pull request template.
6. A maintainer will review within a few business days.

---

Thank you for your contribution!
