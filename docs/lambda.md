# Lambda

## Description
Scripts for managing AWS Lambda functions.

## Scripts

### create_function.py
Creates a Lambda function from an in-memory zip with a stub handler.

```bash
python services/lambda_fn/create_function.py --function-name my-func --role-arn arn:aws:iam::123456789012:role/LambdaRole
python services/lambda_fn/create_function.py --function-name my-func --runtime python3.11 --role-arn arn:aws:iam::123456789012:role/LambdaRole
```

### list_functions.py
```bash
python services/lambda_fn/list_functions.py
```

### invoke_function.py
```bash
python services/lambda_fn/invoke_function.py --function-name my-func
python services/lambda_fn/invoke_function.py --function-name my-func --payload '{"key": "value"}'
```

### delete_function.py
```bash
python services/lambda_fn/delete_function.py --function-name my-func
python services/lambda_fn/delete_function.py --function-name my-func --dry-run
```
