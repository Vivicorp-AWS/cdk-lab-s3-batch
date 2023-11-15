from aws_cdk import (
    NestedStack,
    aws_lambda as _lambda,
    aws_lambda_event_sources as eventsources,
    aws_s3 as s3,
    RemovalPolicy,
    CfnOutput,
)
from aws_cdk.aws_batch import JobQueue, JobDefinition
from aws_cdk.aws_s3 import Bucket
from constructs import Construct

class LambdaStack(NestedStack):

    def __init__(
            self,
            scope: Construct,
            id: str,
            job_queue_arn: str,
            job_definition_arn: str,
            bucket_destination_name: str,
            bucket_source: Bucket,
            **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create Lambda layer
        layer = _lambda.LayerVersion(
            self, 'helper_layer',
            code=_lambda.Code.from_asset("layer"),
            description='Common helper utility',
            compatible_runtimes=[
                _lambda.Runtime.PYTHON_3_9,
                _lambda.Runtime.PYTHON_3_10,
                _lambda.Runtime.PYTHON_3_11],
            removal_policy=RemovalPolicy.DESTROY
            )
        
        function = _lambda.Function(
            self, "lambda_function",
            runtime=_lambda.Runtime.PYTHON_3_10,
            layers=[layer],
            handler="index.handler",
            code=_lambda.Code.from_asset("src/lambda_fn"),
            environment={
                "JOB_QUEUE_ARN", job_queue_arn,
                "JOB_DEFINITION_ARN", job_definition_arn,
                "BUCKET_DESTINATION", bucket_destination_name,
                },
            )
        
        function.add_event_source(
            source=eventsources.S3EventSource(
                bucket=bucket_source,
                events=[
                    s3.EventType.OBJECT_CREATED,
                    ],
                ),
            ),
        
        # [TODO] I'm not sure if this is necessary
        bucket_source.grant_read(function)

        CfnOutput(self, "LambdaFunctionARN", value=function.function_arn)
        CfnOutput(self, "LambdaFunctionName", value=function.function_name)