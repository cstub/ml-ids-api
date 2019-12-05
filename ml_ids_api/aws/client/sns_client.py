import boto3


class AwsSNSClient(object):

    def __init__(self, access_key, secret_key, region):
        self.client = boto3.client('sns',
                                   aws_access_key_id=access_key,
                                   aws_secret_access_key=secret_key,
                                   region_name=region)

    def publish(self, topic, message, attrs):
        self.client.publish(TopicArn=topic,
                            Message=message,
                            MessageAttributes=attrs)
