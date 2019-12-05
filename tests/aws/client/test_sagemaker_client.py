import pytest
import pandas as pd
import responses
import pandas.util.testing as pdu

from ml_ids_api.aws.client.sagemaker_client import AwsSagemakerHttpClient, AwsSagemakerHttpClientError
from ml_ids_api.util.constants import HttpHeaders, MimeTypes

PREDICTIONS = [0, 1, 0]
SAGEMAKER_URL = 'http://sagemaker.aws.com/invocations'


@pytest.fixture
def test_data():
    return pd.DataFrame(data=[1, 2, 3], columns=['feature'])


@pytest.fixture
def test_data_json(test_data):
    return test_data.to_json(orient='split', index=False).encode('utf-8')


@pytest.fixture
def api_success_response():
    with responses.RequestsMock() as rsps:
        rsps.add(method=responses.POST,
                 url=SAGEMAKER_URL,
                 json=PREDICTIONS,
                 status=200)
        yield rsps


@pytest.fixture
def api_server_error_response():
    with responses.RequestsMock() as rsps:
        rsps.add(method=responses.POST,
                 url=SAGEMAKER_URL,
                 json={'error': 'server-error'},
                 status=500)
        yield rsps


@pytest.fixture
def api_client_error_response():
    with responses.RequestsMock() as rsps:
        rsps.add(method=responses.POST,
                 url=SAGEMAKER_URL,
                 json={'error': 'client-error'},
                 status=400)
        yield rsps


@pytest.fixture
def client():
    return AwsSagemakerHttpClient(access_key='ACCESS_KEY',
                                  secret_key='SECRET_KEY',
                                  schema='http',
                                  host='sagemaker.aws.com',
                                  endpoint='/invocations',
                                  region='eu-west-1')


def test_post_invocations_must_invoke_endoint(api_success_response, client, test_data_json):
    client.post_invocations(test_data_json)

    assert len(api_success_response.calls) == 1


def test_post_invocations_must_set_content_type_json_pandas(api_success_response, client, test_data_json):
    client.post_invocations(test_data_json)

    assert len(api_success_response.calls) == 1
    assert api_success_response.calls[0].request.headers[HttpHeaders.CONTENT_TYPE] \
           == MimeTypes.APPLICATION_JSON_PANDAS_SPLIT


def test_post_invocations_must_send_body_in_pandas_json_split_format(api_success_response,
                                                                     client,
                                                                     test_data,
                                                                     test_data_json):
    client.post_invocations(test_data_json)

    assert len(api_success_response.calls) == 1

    request_body = api_success_response.calls[0].request.body
    body_as_df = pd.read_json(request_body, orient='split', convert_dates=False)

    pdu.assert_frame_equal(test_data, body_as_df)


def test_post_invocations_must_return_predictions_on_success(api_success_response, client, test_data_json):
    predictions = client.post_invocations(test_data_json)

    assert len(api_success_response.calls) == 1
    assert predictions == PREDICTIONS


def test_post_invocations_must_raise_error_on_server_error(api_server_error_response, client, test_data_json):
    with pytest.raises(AwsSagemakerHttpClientError):
        client.post_invocations(test_data_json)


def test_post_invocations_must_raise_error_on_client_error(api_client_error_response, client, test_data_json):
    with pytest.raises(AwsSagemakerHttpClientError):
        client.post_invocations(test_data_json)
