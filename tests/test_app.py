import pytest
import pandas as pd
import pandas.util.testing as pdu

from unittest.mock import MagicMock

from ml_ids_api.app import create_flask_app, register_api_endpoints
from ml_ids_api.aws.client.sagemaker_client import AwsSagemakerHttpClient, AwsSagemakerHttpClientError
from ml_ids_api.messaging import SNSMessageProducer
from ml_ids_api.util.constants import HttpHeaders, MimeTypes


@pytest.fixture
def test_data():
    return pd.DataFrame(data=[1, 2, 3], columns=['feature'])


@pytest.fixture
def test_data_json(test_data):
    return test_data.to_json(orient='split', index=False)


@pytest.fixture
def sagemaker_client_mock():
    client = AwsSagemakerHttpClient(None, None, '', '', '', '')
    client.post_invocations = MagicMock(return_value=[0, 1, 0])
    return client


@pytest.fixture
def sns_producer_mock():
    producer = SNSMessageProducer(client=None, topic=None)
    producer.publish_predictions = MagicMock()
    return producer


@pytest.fixture
def client(sagemaker_client_mock, sns_producer_mock):
    app = create_flask_app('config.TestConfig')
    app.config['TESTING'] = True

    register_api_endpoints(app, sagemaker_client_mock, sns_producer_mock)

    with app.test_client() as client:
        yield client


def post_predictions(client, headers=None, data=None):
    return client.post('/api/predictions', headers=headers, data=data)


def test_root(client):
    res = client.get('/')

    assert res.data == b'ML-IDS API'


def test_predictions_when_no_content_type_given_must_return_unsupported_media_type(client, test_data_json):
    res = post_predictions(client,
                           headers={},
                           data=test_data_json)

    assert res.status_code == 415


def test_predictions_when_invalid_content_type_given_must_return_unsupported_media_type(client, test_data_json):
    res = post_predictions(client,
                           headers={HttpHeaders.CONTENT_TYPE: 'text/plain'},
                           data=test_data_json)

    assert res.status_code == 415


def test_predictions_when_no_request_body_given_must_return_bad_request(client, test_data_json):
    res = post_predictions(client,
                           headers={HttpHeaders.CONTENT_TYPE: MimeTypes.APPLICATION_JSON_PANDAS_SPLIT})

    assert res.status_code == 400


def test_predictions_when_invalid_request_body_given_must_return_bad_request(client, test_data_json):
    res = post_predictions(client,
                           headers={HttpHeaders.CONTENT_TYPE: MimeTypes.APPLICATION_JSON_PANDAS_SPLIT},
                           data='i_am_invalid')

    assert res.status_code == 400


def test_predictions_must_return_predictions(client, sagemaker_client_mock, test_data_json):
    sagemaker_client_mock.post_invocations = MagicMock(return_value=[0, 1, 0])

    res = post_predictions(client,
                           headers={HttpHeaders.CONTENT_TYPE: MimeTypes.APPLICATION_JSON_PANDAS_SPLIT},
                           data=test_data_json)

    assert res.status_code == 200
    assert res.json == [0, 1, 0]


def test_predictions_must_send_notifications(client,
                                             sagemaker_client_mock,
                                             sns_producer_mock,
                                             test_data,
                                             test_data_json):
    predictions = [0, 1, 0]
    sagemaker_client_mock.post_invocations = MagicMock(return_value=predictions)

    post_predictions(client,
                     headers={HttpHeaders.CONTENT_TYPE: MimeTypes.APPLICATION_JSON_PANDAS_SPLIT},
                     data=test_data_json)

    sns_producer_mock.publish_predictions.assert_called_once()
    df = sns_producer_mock.publish_predictions.call_args[0][0]

    pdu.assert_series_equal(df['prediction'], pd.Series(data=predictions, name='prediction'))
    pdu.assert_frame_equal(df.drop(columns=['prediction']), test_data)


def test_predictions_when_sagemaker_request_fails_must_return_internal_server_error(client,
                                                                                    test_data_json,
                                                                                    sagemaker_client_mock):
    sagemaker_client_mock.post_invocations = MagicMock(side_effect=AwsSagemakerHttpClientError('Failed'))

    res = post_predictions(client,
                           headers={HttpHeaders.CONTENT_TYPE: MimeTypes.APPLICATION_JSON_PANDAS_SPLIT},
                           data=test_data_json)

    assert res.status_code == 500


def test_predictions_when_sns_request_fails_must_return_internal_server_error(client,
                                                                              test_data_json,
                                                                              sns_producer_mock):
    sns_producer_mock.publish_predictions = MagicMock(side_effect=IOError('Failed'))

    res = post_predictions(client,
                           headers={HttpHeaders.CONTENT_TYPE: MimeTypes.APPLICATION_JSON_PANDAS_SPLIT},
                           data=test_data_json)

    print(res.data)
    assert res.status_code == 500
