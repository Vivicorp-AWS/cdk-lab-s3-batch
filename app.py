#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.top_stack import TopStack
from stacks.ecr_stack import ECRStack
from stacks.batchcompute_stack import BatchComputeStack

app = cdk.App()

# Create stacks
top_stack = TopStack(
    app, f"cdklab-s3batch",
    description="CDK S3 & Batch Lab Top Stack",
)

ecr_stack = ECRStack(
    top_stack, f"ecr-stack",
    description="CDK S3 & Batch Lab ECR Stack",
)

docker_image_asset = ecr_stack.docker_image_asset

batchcompute_stack = BatchComputeStack(
    top_stack, f"batchcompute-stack",
    description="CDK S3 & Batch Lab Batch Compute Stack",
    docker_image_asset=docker_image_asset,
)

batchcompute_stack.add_dependency(ecr_stack)

app.synth()
