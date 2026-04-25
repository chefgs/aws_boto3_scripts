# Route 53

## Description
Scripts for managing Route 53 hosted zones and DNS records.

## Scripts

### create_hosted_zone.py
```bash
python services/route53/create_hosted_zone.py --name example.com
python services/route53/create_hosted_zone.py --name internal.example.com --private
```

### list_hosted_zones.py
```bash
python services/route53/list_hosted_zones.py
```

### create_record.py
```bash
python services/route53/create_record.py --zone-id Z1234567890 --name www.example.com --type A --value 1.2.3.4
python services/route53/create_record.py --zone-id Z1234567890 --name api.example.com --type CNAME --value api.internal.example.com --ttl 60
```

### list_records.py
```bash
python services/route53/list_records.py --zone-id Z1234567890
```

### delete_hosted_zone.py
```bash
python services/route53/delete_hosted_zone.py --zone-id Z1234567890
python services/route53/delete_hosted_zone.py --zone-id Z1234567890 --dry-run
```
