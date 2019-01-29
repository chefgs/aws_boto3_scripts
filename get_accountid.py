import boto3
import sys

# Script gets the AWS profile name as input param and 
# prints the corresponding account-id associated with the profile
session = boto3.Session(profile_name=sys.argv[1])
credentials = session.get_credentials()

# credentials = credentials.get_frozen_credentials()
ACCESS_KEY = credentials.access_key
SECRET_KEY = credentials.secret_key

client = boto3.client("sts", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
account_id = client.get_caller_identity()["Account"]
print(account_id)
