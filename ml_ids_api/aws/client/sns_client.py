import boto3


class AwsSNSClient(object):

    def __init__(self, access_key, secret_key, region):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.client = None

    def initialize(self):
        self.client = boto3.client('sns',
                                   aws_access_key_id=self.access_key,
                                   aws_secret_access_key=self.secret_key,
                                   region_name=self.region)

    def publish(self, topic, message, attrs):
        self.client.publish(TopicArn=topic,
                            Message=message,
                            MessageAttributes=attrs)
