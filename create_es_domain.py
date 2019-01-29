# Script creates the 'n' number of ES doamins

import boto3
import random
import sys
import json

# Total number of ES domains to be created
count = int(sys.argv[2])

# Fetch the account ID associated with the profile name passed as input arg
session = boto3.Session(profile_name=sys.argv[1])
credentials = session.get_credentials()
# credentials = credentials.get_frozen_credentials()
ACCESS_KEY = credentials.access_key
SECRET_KEY = credentials.secret_key

client = boto3.client("sts", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
account_id = client.get_caller_identity()["Account"]
print(account_id)

boto3.setup_default_session(profile_name=sys.argv[1])

for i in range(0, count):
 es = boto3.client('es')
 random_num = random.randint(0,3002)
 es_name = 'demoes' + str(random_num)
 print(es_name)
 policy_data={
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "*"
        ]
      },
      "Action": [
        "es:*"
      ],
      "Resource": "arn:aws:es:us-west-2:"+account_id+":domain/"+es_name+"/*"
    }
  ]
 } 
 policy_json=json.dumps(policy_data)
 
 # Create ES domain with minimum required params
 es_data = es.create_elasticsearch_domain(
    DomainName=str(es_name),
	ElasticsearchVersion='2.3',
	ElasticsearchClusterConfig={
	'InstanceType': 't2.micro.elasticsearch',
	'InstanceCount': 1,
	'DedicatedMasterEnabled': False,
	'ZoneAwarenessEnabled': False
	},
	EBSOptions={
	'EBSEnabled': True,
	'VolumeType': 'standard',
    'VolumeSize': 10
	},
	AccessPolicies=str(policy_json)
 )
 print ("Elastic Search: ", es_data)
