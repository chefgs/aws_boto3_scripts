# SSM — Systems Manager Parameter Store

## Description
Scripts for managing SSM Parameter Store parameters.

## Scripts

### put_parameter.py
```bash
python services/ssm/put_parameter.py --name /myapp/db-host --value db.example.com
python services/ssm/put_parameter.py --name /myapp/db-password --value "secret" --type SecureString
```

### get_parameter.py
```bash
python services/ssm/get_parameter.py --name /myapp/db-host
python services/ssm/get_parameter.py --name /myapp/db-password --with-decryption
```

### list_parameters.py
```bash
python services/ssm/list_parameters.py
python services/ssm/list_parameters.py --path /myapp
```

### delete_parameter.py
```bash
python services/ssm/delete_parameter.py --name /myapp/db-host
python services/ssm/delete_parameter.py --name /myapp/db-host --dry-run
```
