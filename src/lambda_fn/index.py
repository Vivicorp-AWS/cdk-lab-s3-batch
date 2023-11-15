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
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        logger.info(f"## Bucket Name = {bucket_name}")
        logger.info(f"## Object Key = {object_key}")
    
    batch = boto3.client('batch')

    response = batch.submit_job(
        jobName="ObjectProcessJob",
        jobQueue=JOB_QUEUE_ARN,
        jobDefinition=JOB_DEFINITION_ARN,
        containerOverrides={
            "command": ["/app/process.sh", bucket_name, object_key, BUCKET_DESTINATION],
            # "environment": [
            #     {"name": "BUCKET_NAME_SOURCE", "value": bucket_name},
            #     {"name": "OBJECT_KEY", "value": object_key},
            #     {"name": "BUCKET_DESTINATION", "value": BUCKET_DESTINATION}
            # ]
        })