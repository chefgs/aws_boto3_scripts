# Roadmap

This document outlines planned improvements and new features for `aws_boto3_scripts`.

Items are loosely ordered by priority. Community contributions are welcome for any item.

---

## Near-Term

- [ ] **Expand test coverage** — add moto tests for VPC, RDS, Lambda, CloudWatch, CloudFormation, Route 53, ECR, Auto Scaling, ElastiCache, Cognito
- [ ] **Flake8 → Ruff migration** — faster linting with Ruff
- [ ] **Type hints** — add type annotations to all `utils/` and service modules
- [ ] **`--output` flag** — support `--output json|table|csv` on all list/describe scripts
- [ ] **Pagination support** — handle AWS paginated responses automatically in list scripts

## Medium-Term

- [ ] **Config file support** — allow a `~/.aws_boto3_scripts.yaml` for default profile/region
- [ ] **Batch operations** — bulk create/delete from a YAML/JSON manifest file
- [ ] **Additional services** — Kinesis, Step Functions, EventBridge, CodeBuild, Glue
- [ ] **Cost estimation** — add rough cost-per-resource estimates to create scripts
- [ ] **Tagging helper** — shared `--tags` argument to apply consistent tags to all created resources

## Long-Term

- [ ] **Interactive mode** — a TUI (Textual or Rich) for browsing and managing resources
- [ ] **Terraform export** — generate Terraform HCL from live AWS resources
- [ ] **GitHub Actions example workflows** — sample workflows that use these scripts for deployment automation
- [ ] **Container image** — publish a Docker image with all dependencies pre-installed

---

## Completed

- [x] Core scripts for 20+ AWS services
- [x] Shared utilities (session, args, logging)
- [x] moto-based unit tests
- [x] Dry-run mode for destructive operations
- [x] Per-service documentation
- [x] Open source repository hygiene (LICENSE, CONTRIBUTING, SECURITY, etc.)

---

Have an idea? Open a [feature request](https://github.com/chefgs/aws_boto3_scripts/issues/new?template=feature_request.md).
