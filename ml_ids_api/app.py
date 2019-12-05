from flask import Flask, request, make_response, jsonify

from ml_ids_api.util.response_utils import response_invalid_content_type, response_no_request_body, \
    response_deserialization_error, response_error
from ml_ids_api.util.validation_utils import is_valid_content_type
from ml_ids_api.data import deserialize_dataframe, merge_predictions
from ml_ids_api.aws.client.sagemaker_client import AwsSagemakerHttpClient, AwsSagemakerHttpClientError
from ml_ids_api.aws.client.sns_client import AwsSNSClient
from ml_ids_api.messaging import SNSMessageProducer

PREDICT_CONTENT_TYPE = 'application/json; format=pandas-split'


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    sagemaker_client = create_sagemaker_client(app.config)
    sns_client = create_sns_client(app.config)
    sns_message_publisher = SNSMessageProducer(client=sns_client, topic=app.config['AWS_SNS_PREDICTIONS_TOPIC'])

    @app.route('/')
    def index():
        return 'ML-IDS API'

    @app.route('/api/predictions', methods=['POST'])
    def predict():
        content_type = request.headers['Content-Type']

        if not is_valid_content_type(content_type, PREDICT_CONTENT_TYPE):
            return response_invalid_content_type(content_type, PREDICT_CONTENT_TYPE)

        if not request.data:
            return response_no_request_body()

        try:
            request_body = request.data

            data = deserialize_dataframe(request_body)
            predictions = sagemaker_client.post_invocations(request_body)

            data_predictions = merge_predictions(data, predictions)
            sns_message_publisher.publish_predictions(data_predictions)

            return make_response(jsonify(predictions), 200)
        except ValueError as err:
            return response_deserialization_error(err)
        except AwsSagemakerHttpClientError as http_err:
            return response_error(500, str(http_err))

    return app


def create_sagemaker_client(config):
    return AwsSagemakerHttpClient(access_key=config['AWS_ACCESS_KEY'],
                                  secret_key=config['AWS_SECRET_KEY'],
                                  schema='https',
                                  host=config['AWS_SAGEMAKER_HOST'],
                                  endpoint=config['AWS_SAGEMAKER_ENDPOINT'],
                                  region=config['AWS_REGION'])


def create_sns_client(config):
    return AwsSNSClient(access_key=config['AWS_ACCESS_KEY'],
                        secret_key=config['AWS_SECRET_KEY'],
                        region=config['AWS_REGION'])


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0')
