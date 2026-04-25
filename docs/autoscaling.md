# Auto Scaling

## Description
Scripts for managing EC2 Auto Scaling groups.

## Scripts

### create_asg.py
```bash
python services/autoscaling/create_asg.py \
  --name my-asg \
  --launch-template-id lt-0123456789abcdef0 \
  --min 1 --max 5 --desired 2 \
  --subnets subnet-aaa,subnet-bbb
```

### list_asgs.py
```bash
python services/autoscaling/list_asgs.py
```

**Expected output:**
```
[INFO] ASG: my-asg | min=1 max=5 desired=2
```

### delete_asg.py
```bash
python services/autoscaling/delete_asg.py --name my-asg
python services/autoscaling/delete_asg.py --name my-asg --force
python services/autoscaling/delete_asg.py --name my-asg --dry-run
```
