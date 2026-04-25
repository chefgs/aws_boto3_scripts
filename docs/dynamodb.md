# DynamoDB

## Description
Scripts for managing DynamoDB tables and items.

## Scripts

### create_table.py
```bash
python services/dynamodb/create_table.py --table-name Users --partition-key userId
python services/dynamodb/create_table.py --table-name Orders --partition-key orderId --sort-key createdAt
```

### list_tables.py
```bash
python services/dynamodb/list_tables.py
```

### put_item.py
```bash
python services/dynamodb/put_item.py --table-name Users --item '{"userId": {"S": "u1"}, "name": {"S": "Alice"}}'
```

### get_item.py
```bash
python services/dynamodb/get_item.py --table-name Users --key '{"userId": {"S": "u1"}}'
```

### delete_table.py
```bash
python services/dynamodb/delete_table.py --table-name Users
python services/dynamodb/delete_table.py --table-name Users --dry-run
```
