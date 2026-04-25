# Cognito — User Pools

## Description
Scripts for managing Cognito user pools and users.

## Scripts

### create_user_pool.py
```bash
python services/cognito/create_user_pool.py --pool-name MyAppUsers
```

### list_user_pools.py
```bash
python services/cognito/list_user_pools.py
```

### create_user.py
```bash
python services/cognito/create_user.py --pool-id us-east-1_ABC123 --username alice --email alice@example.com
```

### list_users.py
```bash
python services/cognito/list_users.py --pool-id us-east-1_ABC123
```

**Expected output:**
```
[INFO] User: alice | status=FORCE_CHANGE_PASSWORD
```

### delete_user_pool.py
```bash
python services/cognito/delete_user_pool.py --pool-id us-east-1_ABC123
python services/cognito/delete_user_pool.py --pool-id us-east-1_ABC123 --dry-run
```
