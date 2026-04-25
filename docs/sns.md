# SNS — Simple Notification Service

## Description
Scripts for managing SNS topics, subscriptions, and message publishing.

## Scripts

### create_topic.py
```bash
python services/sns/create_topic.py --name my-alerts
```

### list_topics.py
```bash
python services/sns/list_topics.py
```

### publish_message.py
```bash
python services/sns/publish_message.py --topic-arn arn:aws:sns:us-east-1:123456789012:my-alerts --message "Deploy complete"
python services/sns/publish_message.py --topic-arn arn:aws:sns:us-east-1:123456789012:my-alerts --message "Alert!" --subject "System Alert"
```

### subscribe.py
```bash
python services/sns/subscribe.py --topic-arn arn:aws:sns:us-east-1:123456789012:my-alerts --protocol email --endpoint ops@example.com
python services/sns/subscribe.py --topic-arn arn:aws:sns:us-east-1:123456789012:my-alerts --protocol sqs --endpoint arn:aws:sqs:us-east-1:123456789012:my-queue
```

### delete_topic.py
```bash
python services/sns/delete_topic.py --topic-arn arn:aws:sns:us-east-1:123456789012:my-alerts
python services/sns/delete_topic.py --topic-arn arn:aws:sns:us-east-1:123456789012:my-alerts --dry-run
```
