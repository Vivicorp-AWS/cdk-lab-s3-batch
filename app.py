#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.top_stack import TopStack
from stacks.ecr_stack import ECRStack
from stacks.s3_stack import S3Stack
from stacks.batch_stack import BatchStack
from stacks.lambda_stack import LambdaStack

app = cdk.App()

# Create stacks
top_stack = TopStack(
    app, f"cdklab-top-stack",
    description="CDK S3 & Batch Lab Top Stack",
)

ecr_stack = ECRStack(
    top_stack, f"cdklab-ecr-stack",
    description="CDK S3 & Batch Lab ECR Stack",
)

docker_image_asset = ecr_stack.docker_image_asset
# [TODO] ?
# self.docker_image.repository.grantPull(principal)

s3_stack = S3Stack(
    top_stack, f"cdklab-s3-stack",
    description="CDK S3 & Batch Lab S3 Stack",
)
bucket_source = s3_stack.bucket_source
bucket_destination = s3_stack.bucket_destination
bucket_destination_name = bucket_destination.bucket_name

batch_stack = BatchStack(
    top_stack, f"cdklab-batch-stack",
    description="CDK S3 & Batch Lab Batch Stack",
    docker_image_asset=docker_image_asset,
    bucket_source=bucket_source,
    bucket_destination=bucket_destination,
)
job_queue_arn = batch_stack.job_queue.job_queue_arn
job_definition_arn = batch_stack.job_definition.job_definition_arn

# lambda_stack = LambdaStack(
#     top_stack, f"cdklab-lambda-stack",
#     description="CDK S3 & Batch Lab Lambda Stack",
#     job_queue_arn=job_queue_arn,
#     job_definition_arn=job_definition_arn,
#     bucket_destination_name=bucket_destination_name,
#     bucket_source=bucket_source,
# )

# batch_stack.add_dependency(s3_stack)
# batch_stack.add_dependency(ecr_stack)
# lambda_stack.add_dependency(batch_stack)

app.synth()
