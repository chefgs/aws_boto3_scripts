# Secrets Manager

## Description
Scripts for managing secrets in AWS Secrets Manager.

## Scripts

### create_secret.py
```bash
python services/secretsmanager/create_secret.py --name /myapp/db-password --secret-string "mysecretpassword"
python services/secretsmanager/create_secret.py --name /myapp/api-key --secret-string '{"key":"abc123","env":"prod"}'
```

### get_secret.py
```bash
python services/secretsmanager/get_secret.py --name /myapp/db-password
```

### list_secrets.py
```bash
python services/secretsmanager/list_secrets.py
```

### delete_secret.py
Schedules a secret for deletion with a 30-day recovery window.

```bash
python services/secretsmanager/delete_secret.py --name /myapp/db-password
python services/secretsmanager/delete_secret.py --name /myapp/db-password --dry-run
```
