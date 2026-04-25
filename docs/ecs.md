# ECS — Elastic Container Service

## Description
Scripts for managing ECS clusters: create, list, and delete.

## Scripts

### create_cluster.py
```bash
python services/ecs/create_cluster.py --prefix mycluster --count 2
```

### list_clusters.py
```bash
python services/ecs/list_clusters.py --region us-east-1
```

### delete_cluster.py
```bash
python services/ecs/delete_cluster.py --name mycluster12345
python services/ecs/delete_cluster.py --name mycluster12345 --dry-run
```
