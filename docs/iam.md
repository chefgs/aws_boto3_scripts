# IAM — Identity and Access Management

## Description
Scripts for managing IAM users, roles, and policy attachments.

## Scripts

### create_user.py
```bash
python services/iam/create_user.py --username alice
```

### list_users.py
```bash
python services/iam/list_users.py
```

### delete_user.py
```bash
python services/iam/delete_user.py --username alice
python services/iam/delete_user.py --username alice --dry-run
```

### create_role.py
```bash
python services/iam/create_role.py --role-name MyEC2Role --service ec2.amazonaws.com
python services/iam/create_role.py --role-name MyLambdaRole --service lambda.amazonaws.com
```

### list_roles.py
```bash
python services/iam/list_roles.py
```

### attach_policy.py
Attach a managed policy to a user or role.

```bash
python services/iam/attach_policy.py --target-type user --target-name alice --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
python services/iam/attach_policy.py --target-type role --target-name MyEC2Role --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```
