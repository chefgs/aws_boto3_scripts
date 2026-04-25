# EC2 — Elastic Compute Cloud

## Description
Scripts for managing EC2 instances: create, list, describe, and terminate.

## Prerequisites
- AWS credentials configured
- `pip install -r requirements.txt`

## Scripts

### create_instance.py
Launch one or more EC2 instances.

```bash
python services/ec2/create_instance.py --ami ami-0abcdef1234567890 --key-name my-key
python services/ec2/create_instance.py --ami ami-0abcdef1234567890 --key-name my-key --instance-type t3.micro --count 2 --region us-west-2
```

### list_instances.py
List all EC2 instances, optionally filtered by state.

```bash
python services/ec2/list_instances.py
python services/ec2/list_instances.py --state running
python services/ec2/list_instances.py --state stopped --profile prod
```

### describe_instance.py
Describe a single EC2 instance.

```bash
python services/ec2/describe_instance.py --instance-id i-1234567890abcdef0
```

### delete_instance.py
Terminate an EC2 instance. Use `--dry-run` to preview.

```bash
python services/ec2/delete_instance.py --instance-id i-1234567890abcdef0
python services/ec2/delete_instance.py --instance-id i-1234567890abcdef0 --dry-run
```
