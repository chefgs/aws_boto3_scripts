# CloudWatch

## Description
Scripts for managing CloudWatch alarms and metrics.

## Scripts

### create_alarm.py
```bash
python services/cloudwatch/create_alarm.py --alarm-name HighCPU --metric CPUUtilization --namespace AWS/EC2 --threshold 80
python services/cloudwatch/create_alarm.py --alarm-name LowDisk --metric FreeStorageSpace --namespace AWS/RDS --threshold 1000000000 --comparison LessThanThreshold
```

### list_alarms.py
```bash
python services/cloudwatch/list_alarms.py
```

### put_metric_data.py
```bash
python services/cloudwatch/put_metric_data.py --namespace MyApp --metric-name RequestCount --value 42 --unit Count
```

### list_metrics.py
```bash
python services/cloudwatch/list_metrics.py
python services/cloudwatch/list_metrics.py --namespace AWS/EC2
```
