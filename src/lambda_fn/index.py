import logging
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

JOB_QUEUE_ARN = os.environ['JOB_QUEUE_ARN']
JOB_DEFINITION_ARN = os.environ['JOB_DEFINITION_ARN']
BUCKET_DESTINATION = os.environ['BUCKET_DESTINATION']

def handler(event, context):
    for record in event['Records']:
        BUCKET_NAME = record['s3']['bucket']['name']
        OBJECT_KEY = record['s3']['object']['key']
        logger.info(f"## Bucket Name = {BUCKET_NAME}")
        logger.info(f"## Object Key = {OBJECT_KEY}")
    
    batch = boto3.client('batch')

    response = batch.submit_job(
        jobName="ObjectProcessJob",
        jobQueue=JOB_QUEUE_ARN,
        jobDefinition=JOB_DEFINITION_ARN,
        containerOverrides={
            "command": [f"/app/process.sh {BUCKET_NAME} {OBJECT_KEY} {BUCKET_DESTINATION}"],
            # "environment": [
            #     {"name": "BUCKET_NAME_SOURCE", "value": BUCKET_NAME},
            #     {"name": "OBJECT_KEY", "value": OBJECT_KEY},
            #     {"name": "BUCKET_DESTINATION", "value": BUCKET_DESTINATION}
            # ]
        })