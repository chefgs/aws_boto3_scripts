# Boto3 script for creating "n" number S3 buckets in AWS account
# Script can be executed as below,
# This command creates 2 buckets in default aws  profile
# python create_bucket.py default 2 
# This command creates 2 buckets in account2 aws profile
# python create_bucket.py account2 2 

import boto3
import random
import sys

boto3.setup_default_session(profile_name=sys.argv[1])
count = int(sys.argv[2])

for i in range(0, count):
 random_num = random.randint(0,2002)
 s3 = boto3.client('s3')
 bucket = s3.create_bucket( Bucket='prfacct' + str(random_num),
 ACL='private',
 CreateBucketConfiguration={
         'LocationConstraint': 'us-west-2'}
 )
 print ("S3 Bucket: ", bucket)

# s3 = boto3.resource('s3')
# another_bucket=s3.Bucket('perfacct' + str(random_num))
# response = another_bucket.create(ACL='private',
# CreateBucketConfiguration={
         # 'LocationConstraint': 'us-west-2'}
# )

# print ("S3 Bucket: ", response)
