# Elasticsearch (Amazon OpenSearch legacy)

## Description
Scripts for managing Amazon Elasticsearch Service domains.

## Scripts

### create_domain.py
```bash
python services/elasticsearch/create_domain.py --name my-es-domain --version 7.10
```

### list_domains.py
```bash
python services/elasticsearch/list_domains.py
```

### delete_domain.py
```bash
python services/elasticsearch/delete_domain.py --name my-es-domain
python services/elasticsearch/delete_domain.py --name my-es-domain --dry-run
```
