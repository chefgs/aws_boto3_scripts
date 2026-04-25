# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, CHANGELOG.md, ROADMAP.md
- GitHub issue templates (bug report, feature request, documentation)
- GitHub pull request template
- `.editorconfig` and `.env.example`
- Improved CI workflow with PR trigger and coverage reporting

---

## [1.0.0] — Initial Release

### Added
- Core service scripts for 20+ AWS services: S3, EC2, ECS, KMS, IAM, VPC, RDS, Lambda, DynamoDB, SNS, SQS, CloudWatch, Secrets Manager, SSM, CloudFormation, Route 53, ECR, Auto Scaling, ElastiCache, Cognito, Elasticsearch
- Shared utilities: `utils/session.py`, `utils/args.py`, `utils/logging_helper.py`
- moto-based unit tests for S3, EC2, ECS, KMS, IAM, DynamoDB, SQS, SNS, Secrets Manager, SSM
- Per-service documentation under `docs/`
- Dry-run mode for all destructive operations
- Makefile targets: `install`, `test`, `lint`
- Legacy root-level scripts preserved for backward compatibility

---

[Unreleased]: https://github.com/chefgs/aws_boto3_scripts/compare/main...HEAD
