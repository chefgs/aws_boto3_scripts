# KMS — Key Management Service

## Description
Scripts for managing KMS customer-managed keys: create, list, and schedule deletion.

## Scripts

### create_key.py
```bash
python services/kms/create_key.py --description "My encryption key" --count 2
```

### list_keys.py
```bash
python services/kms/list_keys.py
```

### delete_key.py
Schedules a key for deletion (7–30 day window).

```bash
python services/kms/delete_key.py --key-id 12345678-1234-1234-1234-123456789012 --pending-days 7
python services/kms/delete_key.py --key-id 12345678-1234-1234-1234-123456789012 --dry-run
```
