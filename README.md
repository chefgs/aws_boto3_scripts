# AWS Boto3 Scripts

<p align="left">
  <a href="https://github.com/chefgs/aws_boto3_scripts/blob/main/LICENSE"><img src="https://img.shields.io/github/license/chefgs/aws_boto3_scripts" alt="License"></a>
  <a href="https://github.com/chefgs/aws_boto3_scripts/actions/workflows/pythonapp.yml"><img src="https://github.com/chefgs/aws_boto3_scripts/actions/workflows/pythonapp.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/chefgs/aws_boto3_scripts/issues"><img src="https://img.shields.io/github/issues/chefgs/aws_boto3_scripts" alt="Issues"></a>
  <a href="https://github.com/chefgs/aws_boto3_scripts/pulls"><img src="https://img.shields.io/github/issues-pr/chefgs/aws_boto3_scripts" alt="Pull Requests"></a>
  <a href="https://github.com/chefgs/aws_boto3_scripts/stargazers"><img src="https://img.shields.io/github/stars/chefgs/aws_boto3_scripts?style=social" alt="Stars"></a>
  <a href="https://github.com/chefgs/aws_boto3_scripts/network/members"><img src="https://img.shields.io/github/forks/chefgs/aws_boto3_scripts?style=social" alt="Forks"></a>
  <a href="https://github.com/chefgs/aws_boto3_scripts/commits/main"><img src="https://img.shields.io/github/last-commit/chefgs/aws_boto3_scripts" alt="Last Commit"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python 3.9+"></a>
  <a href="https://aws.amazon.com/sdk-for-python/"><img src="https://img.shields.io/badge/boto3-%3E%3D1.26-orange" alt="boto3"></a>
</p>

A comprehensive collection of Python scripts for automating AWS resource management using [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html).

> **Why this project exists:** Managing AWS resources through the console is slow and error-prone. This project provides ready-to-use, well-structured Python scripts that cover 20+ AWS services, follow consistent patterns, and are safe to run — including `--dry-run` mode for destructive operations and moto-based tests that require zero real AWS credentials.

---

## Key Features

- **20+ AWS services** covered: S3, EC2, ECS, KMS, IAM, VPC, RDS, Lambda, DynamoDB, SNS, SQS, CloudWatch, Secrets Manager, SSM, CloudFormation, Route 53, ECR, Auto Scaling, ElastiCache, Cognito, Elasticsearch
- **Consistent script structure** — every script follows the same pattern (argparse, logging, error handling)
- **Dry-run mode** on all destructive operations so you can preview changes safely
- **Shared utilities** for session management, logging, and argument parsing
- **Moto-based unit tests** — run the full test suite without any AWS credentials
- **Per-service documentation** under `docs/`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| AWS SDK | boto3 ≥ 1.26, botocore ≥ 1.29 |
| Testing | pytest, moto (AWS mock) |
| Linting | flake8 |
| CI | GitHub Actions |

---

## Getting Started

### Prerequisites

- Python 3.9 or newer
- pip
- AWS credentials configured (for running scripts against real AWS)
  - Not required for running tests (moto mocks all API calls)

### Installation

```bash
git clone https://github.com/chefgs/aws_boto3_scripts.git
cd aws_boto3_scripts
pip install -r requirements.txt
```

Or use the Makefile:

```bash
make install
```

### Configuration

Configure AWS credentials using the AWS CLI:

```bash
aws configure
# or for a named profile:
aws configure --profile myprofile
```

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

All scripts accept `--profile` and `--region` flags:

```bash
python services/s3/list_buckets.py --profile prod --region eu-west-1
```

### Environment Variables

| Variable | Description | Default |
|---|---|---|
| `AWS_PROFILE` | AWS CLI named profile to use | `default` |
| `AWS_DEFAULT_REGION` | AWS region | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | AWS access key (alternative to profile) | — |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key (alternative to profile) | — |

See `.env.example` for a full list.

---

## Service Coverage

| Service | Scripts | Docs |
|---|---|---|
| **S3** | create, list, delete | [docs/s3.md](docs/s3.md) |
| **EC2** | create, list, describe, delete | [docs/ec2.md](docs/ec2.md) |
| **ECS** | create, list, delete | [docs/ecs.md](docs/ecs.md) |
| **KMS** | create, list, schedule-delete | [docs/kms.md](docs/kms.md) |
| **Elasticsearch** | create, list, delete | [docs/elasticsearch.md](docs/elasticsearch.md) |
| **IAM** | users, roles, attach policy | [docs/iam.md](docs/iam.md) |
| **VPC** | create (with subnet/IGW/RT), list, delete | [docs/vpc.md](docs/vpc.md) |
| **RDS** | create, list, delete | [docs/rds.md](docs/rds.md) |
| **Lambda** | create, list, invoke, delete | [docs/lambda.md](docs/lambda.md) |
| **DynamoDB** | tables + put/get item | [docs/dynamodb.md](docs/dynamodb.md) |
| **SNS** | create, list, publish, subscribe, delete | [docs/sns.md](docs/sns.md) |
| **SQS** | create, list, send, receive, delete | [docs/sqs.md](docs/sqs.md) |
| **CloudWatch** | alarms, metrics | [docs/cloudwatch.md](docs/cloudwatch.md) |
| **Secrets Manager** | create, get, list, delete | [docs/secretsmanager.md](docs/secretsmanager.md) |
| **SSM** | put, get, list, delete parameters | [docs/ssm.md](docs/ssm.md) |
| **CloudFormation** | create, list, describe, delete stacks | [docs/cloudformation.md](docs/cloudformation.md) |
| **Route 53** | hosted zones + DNS records | [docs/route53.md](docs/route53.md) |
| **ECR** | create, list, describe, delete | [docs/ecr.md](docs/ecr.md) |
| **Auto Scaling** | create, list, delete ASGs | [docs/autoscaling.md](docs/autoscaling.md) |
| **ElastiCache** | create, list, delete clusters | [docs/elasticache.md](docs/elasticache.md) |
| **Cognito** | user pools + users | [docs/cognito.md](docs/cognito.md) |

---

## Quick Start

### Create an S3 bucket
```bash
python services/s3/create_bucket.py --prefix mybucket --region us-east-1
```

### List EC2 instances
```bash
python services/ec2/list_instances.py --state running
```

### Create a DynamoDB table
```bash
python services/dynamodb/create_table.py --table-name Users --partition-key userId
```

### Put and get a secret
```bash
python services/secretsmanager/create_secret.py --name /myapp/db-pass --secret-string "s3cr3t"
python services/secretsmanager/get_secret.py --name /myapp/db-pass
```

### Publish an SNS message
```bash
python services/sns/create_topic.py --name alerts
python services/sns/publish_message.py --topic-arn <ARN> --message "Hello!"
```

---

## Dry-Run Mode

All destructive scripts support `--dry-run` to preview the action without making changes:

```bash
python services/ec2/delete_instance.py --instance-id i-1234567890abcdef0 --dry-run
python services/s3/delete_bucket.py --name my-bucket --dry-run
python services/rds/delete_db_instance.py --db-id mydb --dry-run
```

---

## Running Tests

Tests use [moto](https://github.com/getmoto/moto) to mock AWS API calls — **no real AWS credentials required**.

```bash
make test
# or directly:
pytest tests/ -v
```

To run with coverage:

```bash
pytest tests/ -v --cov=services --cov=utils --cov-report=term-missing
```

Test coverage includes: S3, EC2, ECS, KMS, IAM, DynamoDB, SQS, SNS, Secrets Manager, SSM.

---

## Usage Examples

### Create an S3 bucket

```bash
python services/s3/create_bucket.py --prefix mybucket --region us-east-1
```

### List EC2 instances

```bash
python services/ec2/list_instances.py --state running
```

### Create a DynamoDB table

```bash
python services/dynamodb/create_table.py --table-name Users --partition-key userId
```

### Store and retrieve a secret

```bash
python services/secretsmanager/create_secret.py --name /myapp/db-pass --secret-string "s3cr3t"
python services/secretsmanager/get_secret.py --name /myapp/db-pass
```

### Publish an SNS message

```bash
python services/sns/create_topic.py --name alerts
python services/sns/publish_message.py --topic-arn <ARN> --message "Hello!"
```

### Create a VPC with subnet, Internet Gateway, and Route Table

```bash
python services/vpc/create_vpc.py --cidr 10.0.0.0/16 --name my-vpc
```

See `docs/` for full per-service usage documentation.

---

## Architecture Overview

```
┌─────────────────────────────────────────────┐
│              aws_boto3_scripts               │
│                                             │
│  services/        ← per-service scripts     │
│    s3/            ← create, list, delete    │
│    ec2/           ← create, list, delete    │
│    ...                                      │
│                                             │
│  utils/           ← shared helpers          │
│    session.py     ← boto3 client/session    │
│    args.py        ← argparse base parser    │
│    logging_helper.py ← structured logging  │
│                                             │
│  tests/           ← moto-based unit tests  │
│  docs/            ← per-service docs       │
└─────────────────────────────────────────────┘
         │
         ▼
   AWS APIs (boto3 / botocore)
         │
         ▼
   Real AWS  ─or─  moto mock (tests)
```

Each service script follows the same pattern:
1. Parse arguments via the shared `utils.args` base parser
2. Obtain a boto3 client via `utils.session.get_client()`
3. Call the AWS API wrapped in `try/except botocore.exceptions.ClientError`
4. Log results via `utils.logging_helper`

---

## Project Structure

```
aws_boto3_scripts/
├── .env.example              # Example environment variables
├── .editorconfig             # Editor settings
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
├── setup.cfg                 # pytest configuration
├── Makefile                  # install / test / lint targets
├── utils/
│   ├── session.py            # shared boto3 client/session helpers
│   ├── logging_helper.py     # structured logging setup
│   └── args.py               # shared argparse base parser
├── services/
│   ├── s3/
│   ├── ec2/
│   ├── ecs/
│   ├── kms/
│   ├── elasticsearch/
│   ├── iam/
│   ├── vpc/
│   ├── rds/
│   ├── lambda_fn/
│   ├── dynamodb/
│   ├── sns/
│   ├── sqs/
│   ├── cloudwatch/
│   ├── secretsmanager/
│   ├── ssm/
│   ├── cloudformation/
│   ├── route53/
│   ├── ecr/
│   ├── autoscaling/
│   ├── elasticache/
│   └── cognito/
├── tests/                    # moto-based unit tests
├── docs/                     # per-service documentation
└── .github/
    ├── workflows/ci.yml      # GitHub Actions CI
    ├── ISSUE_TEMPLATE/       # Issue templates
    └── PULL_REQUEST_TEMPLATE.md
```

---

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features and improvements.

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to submit bug reports, feature requests, and pull requests.

Quick guide:

1. Fork the repository and create a feature branch.
2. Add your script under `services/<service_name>/`.
3. Follow the existing pattern:
   - Import from `utils.session`, `utils.args`, `utils.logging_helper`
   - Expose a callable main function (e.g., `def create_thing(client, ...)`)
   - Wrap AWS calls in `try/except botocore.exceptions.ClientError`
   - Add `--dry-run` to any destructive operation
4. Add a test in `tests/test_<service>.py` using `@mock_aws`.
5. Add or update the doc in `docs/<service>.md`.
6. Run `make test` to verify all tests pass.
7. Open a pull request.

---

## Security

Please do **not** open public GitHub issues for security vulnerabilities. See [SECURITY.md](SECURITY.md) for the responsible disclosure process.

---

## Legacy Scripts

The original root-level scripts are preserved for backward compatibility:

| Script | Description |
|---|---|
| `create_buckets.py` | Original S3 bucket creator |
| `create_ec2.py` | Original EC2 instance creator |
| `create_ecs_cluster.py` | Original ECS cluster creator |
| `create_es_domain.py` | Original Elasticsearch domain creator |
| `create_kms_keys.py` | Original KMS key creator |
| `get_accountid.py` | Get AWS account ID |

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).

---

## Maintainer

**Saravanan G** ([@chefgs](https://github.com/chefgs))

---

## Acknowledgements

- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) — AWS SDK for Python
- [moto](https://github.com/getmoto/moto) — Mock AWS services for testing
- [pytest](https://pytest.org/) — Testing framework
- [flake8](https://flake8.pycqa.org/) — Python linting

