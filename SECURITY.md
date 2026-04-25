# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest (main branch) | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in this project, please report it privately by:

1. Emailing the maintainer directly (see the [GitHub profile](https://github.com/chefgs) for contact details).
2. Or opening a [GitHub Security Advisory](https://github.com/chefgs/aws_boto3_scripts/security/advisories/new).

Please include:
- A description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Any suggested mitigation

You can expect an acknowledgement within **48 hours** and a resolution or status update within **7 days**.

## Security Best Practices When Using This Project

- **Never hardcode AWS credentials** in scripts or commit them to source control.
- Use AWS IAM roles with least-privilege permissions.
- Use named profiles (`aws configure --profile`) or environment variables for credentials.
- Use `--dry-run` before running destructive operations in production.
- Rotate AWS access keys regularly.
- Store secrets in AWS Secrets Manager or SSM Parameter Store, not in `.env` files committed to git.
