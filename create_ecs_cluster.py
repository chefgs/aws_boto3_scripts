# Boto3 script for creating "n" number ECS clusters in AWS account
# Script can be executed as below,
# This command creates 2 ECS in default aws  profile
# python create_ecs.py default 2 
# This command creates 2 ECS keys in account2 aws profile
# python create_ecs.py account2 2 

import boto3
import random
import sys

boto3.setup_default_session(profile_name=sys.argv[1])
count = int(sys.argv[2])

for i in range(0, count):
 ecs = boto3.client('ecs')
 random_num = random.randint(0,2002)
 ecs_data = ecs.create_cluster(
    clusterName='prfecs' + str(random_num)
	#,
	#tags= [{ "key": "prfecskey", "value": "prfecsvalue" }]
 )
 print ("ECS: ", ecs_data)
