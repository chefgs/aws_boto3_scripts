# ElastiCache

## Description
Scripts for managing ElastiCache clusters (Redis and Memcached).

## Scripts

### create_cluster.py
```bash
python services/elasticache/create_cluster.py --cluster-id my-redis --engine redis --node-type cache.t3.micro
python services/elasticache/create_cluster.py --cluster-id my-memcached --engine memcached --num-nodes 2
```

### list_clusters.py
```bash
python services/elasticache/list_clusters.py
```

**Expected output:**
```
[INFO] Cluster: my-redis | engine=redis | status=creating
```

### delete_cluster.py
```bash
python services/elasticache/delete_cluster.py --cluster-id my-redis
python services/elasticache/delete_cluster.py --cluster-id my-redis --dry-run
```
