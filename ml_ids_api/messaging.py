"""
Module providing facilities to publish messages to the Amazon SNS service.
"""
import pandas as pd


class SNSMessageProducer:
    """
    Producer to publish messages to a specified Amazon SNS topic.
    """

    def __init__(self, client, topic):
        self.client = client
        self.topic = topic

    def publish_predictions(self, data: pd.DataFrame) -> None:
        """
        Publish feature data and predictions from the given Pandas DataFrame.

        :param data: Pandas DataFrame containing feature data and predictions.
        :return: None
        """
        for i in range(0, len(data)):
            sample = data.iloc[i:i + 1]

            prediction = 'attack' if sample.iloc[0]['prediction'] == 1 else 'benign'
            message = sample.to_json(orient='split')

            self.client.publish(topic=self.topic,
                                message=message,
                                attrs={
                                    'prediction': {
                                        'DataType': 'String',
                                        'StringValue': prediction
                                    }
                                })
