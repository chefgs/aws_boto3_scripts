# VPC — Virtual Private Cloud

## Description
Scripts for managing VPCs and their networking components.

## Scripts

### create_vpc.py
Creates a VPC with a public subnet, internet gateway, and route table.

```bash
python services/vpc/create_vpc.py --cidr 10.0.0.0/16
python services/vpc/create_vpc.py --cidr 172.16.0.0/16 --region us-west-2
```

**Expected output:**
```
[INFO] Created VPC: vpc-0123456789abcdef0
[INFO] Created subnet: subnet-0123456789abcdef0
[INFO] Created and attached IGW: igw-0123456789abcdef0
[INFO] Created route table: rtb-0123456789abcdef0
```

### list_vpcs.py
```bash
python services/vpc/list_vpcs.py
```

### delete_vpc.py
Deletes a VPC and all its dependencies (subnets, IGWs, route tables).

```bash
python services/vpc/delete_vpc.py --vpc-id vpc-0123456789abcdef0
python services/vpc/delete_vpc.py --vpc-id vpc-0123456789abcdef0 --dry-run
```
