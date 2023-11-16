from aws_cdk import (
    NestedStack,
    aws_ec2 as ec2,
    aws_batch as batch,
    aws_ecs as ecs,
    Size,
    CfnOutput,
)
from aws_cdk.aws_ecr_assets import DockerImageAsset
from aws_cdk.aws_s3 import Bucket
from constructs import Construct

class BatchStack(NestedStack):

    def __init__(
            self,
            scope: Construct,
            id: str,
            docker_image_asset: DockerImageAsset,
            bucket_source: Bucket,
            bucket_destination: Bucket,
            **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

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


        self.job_queue = batch.JobQueue(self, "BatchJobQueue")

        ec2_compute_environment = batch.ManagedEc2EcsComputeEnvironment(self, "BatchEc2ComputeEnv",
            spot=True,
            spot_bid_percentage=75,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )
        # bucket_source.grant_read(ec2_compute_environment.service_role)
        # bucket_destination.grant_write(ec2_compute_environment.service_role)

        self.job_queue.add_compute_environment(ec2_compute_environment, 1)

        self.job_definition = batch.EcsJobDefinition(self, "BatchECSJobDef",
            container=batch.EcsEc2ContainerDefinition(self, "BatchECSEC2ContainerJobDef",
                image=ecs.ContainerImage.from_docker_image_asset(docker_image_asset),
                command=["/app/process.sh",],
                memory=Size.mebibytes(512),
                cpu=1
            )
        )

        CfnOutput(self, "VPCARN", value=vpc.vpc_arn)
        CfnOutput(self, "BatchJobQueueARN", value=self.job_queue.job_queue_arn)
        CfnOutput(self, "BatchJobQueueName", value=self.job_queue.job_queue_name)
        CfnOutput(self, "BatchJobDefinitionARN", value=self.job_definition.job_definition_arn)
        CfnOutput(self, "BatchJobDefinitionName", value=self.job_definition.job_definition_name)