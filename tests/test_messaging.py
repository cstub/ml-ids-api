import pytest
import pandas as pd

from unittest.mock import MagicMock

from ml_ids_api.messaging import SNSMessageProducer
from ml_ids_api.aws.client.sns_client import AwsSNSClient

AWS_TOPIC = 'AWS_TOPIC_ARN'


@pytest.fixture
def test_data():
    return pd.DataFrame(data={'feature': [1, 2, 3], 'prediction': [0, 1, 0]})


@pytest.fixture
def test_data_json(test_data):
    return test_data.to_json(orient='split', index=False)


@pytest.fixture
def sns_client_mock():
    client = AwsSNSClient(access_key='ACCESS_KEY',
                          secret_key='SECRET_KEY',
                          region='eu-west-1')
    client.publish = MagicMock(return_value=None)
    return client


@pytest.fixture
def producer(sns_client_mock):
    return SNSMessageProducer(client=sns_client_mock, topic=AWS_TOPIC)


def assert_publish_prediction_call(args, expected_topic, expected_message, expected_prediction_attribute):
    topic = args['topic']
    message = args['message']
    attrs = args['attrs']

    assert topic == expected_topic
    assert message == expected_message
    assert 'prediction' in attrs
    assert attrs['prediction']['StringValue'] == expected_prediction_attribute


def test_publish_predictions_must_publish_message_per_prediction(producer, test_data, sns_client_mock):
    producer.publish_predictions(test_data)

    sns_client_mock.publish.assert_called()
    assert sns_client_mock.publish.call_count == len(test_data)


def test_publish_predictions_must_publish_message_per_prediction_s(producer, test_data, sns_client_mock):
    producer.publish_predictions(test_data)

    sns_client_mock.publish.assert_called()
    arg_list = sns_client_mock.publish.call_args_list

    assert_publish_prediction_call(args=arg_list[0][1],
                                   expected_topic=AWS_TOPIC,
                                   expected_message=test_data.iloc[0:1].to_json(orient='split'),
                                   expected_prediction_attribute='benign')

    assert_publish_prediction_call(args=arg_list[1][1],
                                   expected_topic=AWS_TOPIC,
                                   expected_message=test_data.iloc[1:2].to_json(orient='split'),
                                   expected_prediction_attribute='attack')

    assert_publish_prediction_call(args=arg_list[2][1],
                                   expected_topic=AWS_TOPIC,
                                   expected_message=test_data.iloc[2:3].to_json(orient='split'),
                                   expected_prediction_attribute='benign')


def test_publish_predictions_when_empty_data_given_must_publish_no_message(producer, sns_client_mock):
    producer.publish_predictions(pd.DataFrame())

    sns_client_mock.publish.assert_not_called()
