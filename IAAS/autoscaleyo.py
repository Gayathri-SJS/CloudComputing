import boto3
import time

AWS_ACCESS_KEY_ID = #access key
AWS_SECRET_ACCESS_KEY = #secret access key

web_sqs = boto3.client('ec2',region_name='us-east-1',aws_access_key_id= AWS_ACCESS_KEY_ID, aws_secret_access_key= AWS_SECRET_ACCESS_KEY)
sqs = boto3.client('sqs',region_name='us-east-1',aws_access_key_id= AWS_ACCESS_KEY_ID, aws_secret_access_key= AWS_SECRET_ACCESS_KEY)

def startInstance(num,instancelist):
    response = web_sqs.start_instances(
    InstanceIds=instancelist[:num]
    )


def stopInstance(instancelist):
    runningList = [i for i in instancelist if web_sqs.describe_instances(InstanceIds=[i])['Reservations'][0]['Instances'][0]['State']['Name'] == 'running']
    if runningList:
        response = web_sqs.stop_instances(
        InstanceIds=runningList
    )


def getRunningInstances():
    response = web_sqs.describe_instances(
    Filters=[
        {
            'Name': 'instance-state-name',
            'Values': [
                'pending',
                'running'
            ]
        },
    ]
    )
    instancelist= [instance['InstanceId'] for reserv in response['Reservations'] for instance in reserv['Instances'] ]
    return instancelist

def getStopInstances():
    response = web_sqs.describe_instances(
    Filters=[
        {
            'Name': 'instance-state-name',
            'Values': [
                'stopping',
                'stopped'
            ]
        },
    ]
    )
    instancelist= [instance['InstanceId'] for reserv in response['Reservations'] for instance in reserv['Instances']  ]
    return instancelist

def getQueueLen():
    response = sqs.get_queue_attributes(
    QueueUrl='https://sqs.us-east-1.amazonaws.com/590183841764/1230360484-req-queue',
    AttributeNames=[
        'ApproximateNumberOfMessages'
    ]
    )
    return int(response['Attributes']['ApproximateNumberOfMessages'])

while True:
    try:
        n=getQueueLen()
        runinstancelist=getRunningInstances()
        runinstancelist.remove("i-02444e1bc75a43723")
        stopinstancelist=getStopInstances()
        if n==0 and len(runinstancelist)>0:
            stopInstance(runinstancelist)
        elif 0<n<=10 and len(runinstancelist)<10:
            req= 10 - len(runinstancelist)
            startInstance(req,stopinstancelist)
        elif n>10 and len(runinstancelist)<20:
            req= 20 - len(runinstancelist)
            startInstance(req,stopinstancelist)
        time.sleep(10)
    except Exception as e:
        print(e)
