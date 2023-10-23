# AWS Boto3 Project
## Getting started with Installation
1.	Install python
2.	Install pip
3.	Add python and pip installation to PATH variable
5.	Install boto3: pip install boto3
6.	Install AWS-CLI: pip install awscli --upgrade --user 
7.	Configure AWS-CLI for linking account using the command : aws configure
## Create Python code and run
9.	Create boto3 script and save the file as <boto3_script_name>.py extension
10.	Run as python <boto3_script_name>.py

## Detailed Instructions
The following steps has been captured from the Boto3 [Getting Started](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) docs.

### Install boto3
Boto3 requires `python` `version 3` or above and python package installer `pip`
- Refer official `python` [download documentation](https://www.python.org/downloads/) to install it.
  - For macos, `brew install python` works good.
  - For Linux, `apt update && apt install python` might be fine.
- Install `pip` using the [official pip install](https://pip.pypa.io/en/stable/installation/) documentation
  - I've used `get-pip.py` [method](https://pip.pypa.io/en/stable/installation/#get-pip-py) to install `pip`
- Install boto3: `pip install boto3` or `python3 pip install boto3`

### AWS CLI
- Install AWS CLI by following the instructions [here in the docs](https://aws.amazon.com/cli/)
- After installing AWS CLI, use `aws configure` command to setup AWS secret key, access key or temporary sts key.
- Read more about the AWS boto3 [configuration here](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html)
- Install AWS-CLI: `pip install awscli --upgrade --user` 

### AWS Common Runtime (Optional)
In addition to the default install of Boto3, you can choose to include the new [AWS Common Runtime (CRT)](https://docs.aws.amazon.com/sdkref/latest/guide/common-runtime.html). The AWS CRT is a collection of modular packages that serve as a new foundation for AWS SDKs. 

### Using Boto3
To use Boto3, you must first import it and indicate which service or services you’re going to use:
```
import boto3
```
