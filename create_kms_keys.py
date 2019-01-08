# Boto3 script for creating "n" number KMS keys in AWS account
# Script can be executed as below,
# This command creates 2 KMS keys in default aws  profile
# python create_kms.py default 2 
# This command creates 2 KMS keys in account2 aws profile
# python create_kms.py account2 2 

import boto3
import random
import sys

boto3.setup_default_session(profile_name=sys.argv[1])
count = int(sys.argv[2])

for i in range(0, count):
 kms = boto3.client('kms')
 kms_data = kms.create_key( Origin='AWS_KMS',
 Tags=[
        {
            'TagKey': 'SampleKmsKey',
            'TagValue': 'SampleKmsKeyValue'
        } ]
 )
 print ("S3 Bucket: ", kms_data)
