# CloudFormation

## Description
Scripts for managing CloudFormation stacks.

## Scripts

### create_stack.py
```bash
python services/cloudformation/create_stack.py --stack-name my-stack --template-file template.yaml
python services/cloudformation/create_stack.py --stack-name my-stack --template-url https://s3.amazonaws.com/my-bucket/template.yaml
python services/cloudformation/create_stack.py --stack-name my-stack --template-file template.yaml --parameters '[{"ParameterKey":"Env","ParameterValue":"prod"}]'
```

### list_stacks.py
```bash
python services/cloudformation/list_stacks.py
python services/cloudformation/list_stacks.py --status-filter CREATE_COMPLETE
```

### describe_stack.py
```bash
python services/cloudformation/describe_stack.py --stack-name my-stack
```

### delete_stack.py
```bash
python services/cloudformation/delete_stack.py --stack-name my-stack
python services/cloudformation/delete_stack.py --stack-name my-stack --dry-run
```
