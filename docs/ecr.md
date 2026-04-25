# ECR — Elastic Container Registry

## Description
Scripts for managing ECR repositories.

## Scripts

### create_repository.py
```bash
python services/ecr/create_repository.py --name my-app
```

### list_repositories.py
```bash
python services/ecr/list_repositories.py
```

### describe_repository.py
```bash
python services/ecr/describe_repository.py --name my-app
```

### delete_repository.py
```bash
python services/ecr/delete_repository.py --name my-app
python services/ecr/delete_repository.py --name my-app --dry-run
```

## Docker Push Example
After creating a repository, authenticate and push an image:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker tag my-app:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/my-app:latest
```
