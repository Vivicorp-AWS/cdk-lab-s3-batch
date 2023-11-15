from aws_cdk import (
    NestedStack,
    aws_s3 as s3,
    RemovalPolicy,
    CfnOutput,
)

from constructs import Construct

class S3Stack(NestedStack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.bucket_source = s3.Bucket(
            self, "FileSourceBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,)
        
        self.bucket_destination = s3.Bucket(
            self, "FileDestinationBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,)
        
        CfnOutput(self, "SourceBucketName", value=self.bucket_source.bucket_name)
        CfnOutput(self, "SourceBucketARN", value=self.bucket_source.bucket_arn)
        CfnOutput(self, "DestinationBucketName", value=self.bucket_destination.bucket_name)
        CfnOutput(self, "DestinationBucketARN", value=self.bucket_destination.bucket_arn)