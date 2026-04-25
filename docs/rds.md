# RDS — Relational Database Service

## Description
Scripts for managing RDS DB instances.

## Scripts

### create_db_instance.py
```bash
python services/rds/create_db_instance.py --db-id mydb --engine mysql --username admin --password secret123
python services/rds/create_db_instance.py --db-id pgdb --engine postgres --db-class db.t3.small --username pgadmin --password pgpass --storage 50
```

### list_db_instances.py
```bash
python services/rds/list_db_instances.py
```

### delete_db_instance.py
```bash
python services/rds/delete_db_instance.py --db-id mydb --skip-final-snapshot
python services/rds/delete_db_instance.py --db-id mydb --dry-run
```
