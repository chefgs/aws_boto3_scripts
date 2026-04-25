# SQS — Simple Queue Service

## Description
Scripts for managing SQS queues and messages.

## Scripts

### create_queue.py
```bash
python services/sqs/create_queue.py --name my-queue
python services/sqs/create_queue.py --name my-fifo-queue --fifo
```

### list_queues.py
```bash
python services/sqs/list_queues.py
```

### send_message.py
```bash
python services/sqs/send_message.py --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue --message "Hello SQS"
```

### receive_messages.py
```bash
python services/sqs/receive_messages.py --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue
python services/sqs/receive_messages.py --queue-url https://... --max-count 5
```

### delete_queue.py
```bash
python services/sqs/delete_queue.py --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/my-queue
python services/sqs/delete_queue.py --queue-url https://... --dry-run
```
