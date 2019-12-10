"""
Module containing classes to interface with the Amazon SNS service (https://aws.amazon.com/sns/).
"""
import boto3


class AwsSNSClient:
    """
    A client to interface with the the Amazon SNS service.
    Can be used to publish new SNS messages.
    """

    def __init__(self, access_key, secret_key, region):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.client = None

    def initialize(self) -> None:
        """
        Initializes the client. Must be invoked before messages can be published.

        :return: None
        """
        self.client = boto3.client('sns',
                                   aws_access_key_id=self.access_key,
                                   aws_secret_access_key=self.secret_key,
                                   region_name=self.region)

    def publish(self, topic: str, message: str, attrs: dict) -> None:
        """
        Publish a new SNS message to the given topic.

        :param topic: ARN of the topic to publish the message.
        :param message: Message to publish.
        :param attrs: Additional message attributes.
        :return: None
        """
        self.client.publish(TopicArn=topic,
                            Message=message,
                            MessageAttributes=attrs)
