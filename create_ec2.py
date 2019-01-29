import boto3

ec2 = boto3.resource(
    service_name='ec2',
    region_name='us-west-2'
)
instances = ec2.create_instances(
        ImageId='ami-07e276df524150',
        InstanceType='t2.micro',
        KeyName='dummy-key',
        MinCount=1,
        MaxCount=1
)
