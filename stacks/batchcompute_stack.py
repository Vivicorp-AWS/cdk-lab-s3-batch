from aws_cdk import (
    NestedStack,
    aws_s3 as s3,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_lambda_event_sources as eventsources,
    aws_ec2 as ec2,
    aws_batch as batch,
    aws_ecs as ecs,
    Size,
    CfnOutput,
)

from constructs import Construct
from aws_cdk.aws_ecr_assets import DockerImageAsset

class BatchComputeStack(NestedStack):

    def __init__(
            self,
            scope: Construct,
            id: str,
            docker_image_asset: DockerImageAsset,
            **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bucket_source = s3.Bucket(
            self, "FileSourceBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,)
        
        bucket_destination = s3.Bucket(
            self, "FileDestinationBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,)
        bucket_destination_name = bucket_destination.bucket_name
        
        # VPC in 2 azs, including 1 public and 1 private subnet in each az
        vpc = ec2.Vpc(
            self, "BatchVPC",
            max_azs=2,
            ip_addresses=ec2.IpAddresses.cidr("10.10.0.0/16"),
            # configuration will create 2 groups in 2 AZs = 4 subnets.
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PUBLIC,
                    name="Public",
                    cidr_mask=24
                    ),
                ec2.SubnetConfiguration(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    name="Private",
                    cidr_mask=24
                    )
                ],
            )
        
        # # If we choose to use Private Subnet: There shouuld be a
        # # Gateway VPC Endpoint for Lambda Function to access S3 
        # self.vpc.add_gateway_endpoint(
        #     "S3GatewayVPCEndpoint",
        #     service=ec2.GatewayVpcEndpointAwsService.S3,
        #     subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)],
        # )

        job_queue = batch.JobQueue(self, "BatchJobQueue")
        job_queue_arn = job_queue.job_queue_arn

        ec2_compute_environment = batch.ManagedEc2EcsComputeEnvironment(self, "BatchEc2ComputeEnv",
            spot=True,
            spot_bid_percentage=75,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )
        bucket_source.grant_read(ec2_compute_environment.instance_role)
        bucket_destination.grant_write(ec2_compute_environment.instance_role)

        job_queue.add_compute_environment(ec2_compute_environment, 1)
        
        job_definition = batch.EcsJobDefinition(self, "BatchECSJobDef",
            container=batch.EcsEc2ContainerDefinition(self, "BatchECSEC2ContainerJobDef",
                image=ecs.ContainerImage.from_docker_image_asset(docker_image_asset),
                command=["/app/process.sh",],
                memory=Size.mebibytes(512),
                cpu=1
            )
        )
        job_definition_arn = job_definition.job_definition_arn
        
        function = _lambda.Function(
            self, "lambda_function",
            runtime=_lambda.Runtime.PYTHON_3_10,
            handler="index.handler",
            code=_lambda.Code.from_asset("src/lambda_fn"),
            environment=dict(
                    JOB_QUEUE_ARN=job_queue_arn,
                    JOB_DEFINITION_ARN=job_definition_arn,
                    BUCKET_DESTINATION=bucket_destination_name,
                )
            )
        function.add_event_source(
            source=eventsources.S3EventSource(
                bucket=bucket_source,
                events=[
                    s3.EventType.OBJECT_CREATED,
                    ],
                ),
            ),
        bucket_source.grant_read(function.role)
        job_definition.grant_submit_job(function.role, job_queue)
        
        CfnOutput(self, "SourceBucketName", value=bucket_source.bucket_name)
        CfnOutput(self, "SourceBucketARN", value=bucket_source.bucket_arn)
        CfnOutput(self, "DestinationBucketName", value=bucket_destination.bucket_name)
        CfnOutput(self, "DestinationBucketARN", value=bucket_destination.bucket_arn)

        CfnOutput(self, "VPCARN", value=vpc.vpc_arn)
        CfnOutput(self, "BatchJobQueueARN", value=job_queue.job_queue_arn)
        CfnOutput(self, "BatchJobQueueName", value=job_queue.job_queue_name)
        CfnOutput(self, "BatchJobDefinitionARN", value=job_definition.job_definition_arn)
        CfnOutput(self, "BatchJobDefinitionName", value=job_definition.job_definition_name)

        CfnOutput(self, "LambdaFunctionARN", value=function.function_arn)
        CfnOutput(self, "LambdaFunctionName", value=function.function_name)

