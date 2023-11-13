import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_lab_s3_batch.cdk_lab_s3_batch_stack import CdkLabS3BatchStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_lab_s3_batch/cdk_lab_s3_batch_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkLabS3BatchStack(app, "cdk-lab-s3-batch")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
