import pandas as pd


class SNSMessageProducer(object):

    def __init__(self, client, topic):
        self.client = client
        self.topic = topic

    def publish_predictions(self, data: pd.DataFrame) -> None:
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
