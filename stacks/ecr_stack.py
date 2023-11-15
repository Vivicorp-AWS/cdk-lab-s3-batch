from aws_cdk import (
    NestedStack,
    CfnOutput,
)
from aws_cdk.aws_ecr_assets import DockerImageAsset, Platform
from constructs import Construct
import os

class ECRStack(NestedStack):

    def __init__(
            self,
            scope: Construct,
            id: str,
            **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.docker_image_asset = DockerImageAsset(self, "ObjectProcess",
            directory=os.path.join("src", "docker"),
            platform=Platform.LINUX_AMD64,
        )

        CfnOutput(self, "ECRImageURI", value=self.docker_image_asset.image_uri)
        CfnOutput(self, "ECRImageTag", value=self.docker_image_asset.image_tag)
        CfnOutput(self, "ECRRepositoryARN", value=self.docker_image_asset.repository.repository_arn)
        CfnOutput(self, "ECRRepositoryName", value=self.docker_image_asset.repository.repository_name)
        CfnOutput(self, "ECRRepositoryURI", value=self.docker_image_asset.repository.repository_uri)

