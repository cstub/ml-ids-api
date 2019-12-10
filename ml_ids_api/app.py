"""
Module containing the REST API for ML-IDS service.
"""
from flask import Flask, request, make_response, jsonify
from werkzeug.exceptions import HTTPException

from ml_ids_api.util.response_utils import invalid_content_type, bad_request_missing_body, \
    bad_request_deserialization_error, response_error
from ml_ids_api.util.validation_utils import is_valid_content_type
from ml_ids_api.util.constants import HttpHeaders, MimeTypes
from ml_ids_api.data import deserialize_dataframe, merge_predictions
from ml_ids_api.aws.client.sagemaker_client import AwsSagemakerHttpClient
from ml_ids_api.aws.client.sns_client import AwsSNSClient
from ml_ids_api.messaging import SNSMessageProducer


def create_app(config_path):
    """
    Creates the Flask application and initializes the HTTP endpoints.

    :param config_path: Path to the configuration file.
    :return: Flask app.
    """
    app = create_flask_app(config_path)
    sagemaker_client = create_sagemaker_client(app.config)
    sns_client = create_sns_client(app.config)
    sns_message_publisher = SNSMessageProducer(client=sns_client, topic=app.config['AWS_SNS_PREDICTIONS_TOPIC'])

    register_api_endpoints(app, sagemaker_client, sns_message_publisher)
    return app


def create_flask_app(config_path):
    """
    Creates the Flask application and loads the configuration.

    :param config_path: Path to the configuration file.
    :return: Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_path)
    return app


def create_sagemaker_client(config):
    """
    Creates the AWS SageMaker client.

    :param config: Application configuration.
    :return: SageMaker client.
    """
    return AwsSagemakerHttpClient(access_key=config['AWS_ACCESS_KEY'],
                                  secret_key=config['AWS_SECRET_KEY'],
                                  schema='https',
                                  host=config['AWS_SAGEMAKER_HOST'],
                                  endpoint=config['AWS_SAGEMAKER_ENDPOINT'],
                                  region=config['AWS_REGION'])


def create_sns_client(config):
    """
    Creates the AWS SNS client.

    :param config: Application configuration.
    :return: SageMaker client.
    """
    client = AwsSNSClient(access_key=config['AWS_ACCESS_KEY'],
                          secret_key=config['AWS_SECRET_KEY'],
                          region=config['AWS_REGION'])
    client.initialize()
    return client


def register_api_endpoints(app, sagemaker_client, sns_message_producer):
    """
    Registers the API HTTP endpoints.

    :param app: Flask application.
    :param sagemaker_client: AWS SageMaker client.
    :param sns_message_producer: AWS SNS client.
    :return: None
    """

    @app.errorhandler(Exception)
    def handle_exception(err):
        if isinstance(err, HTTPException):
            return err
        return response_error(500, str(err))

    @app.route('/')
    def root():
        return 'ML-IDS API'

    @app.route('/api/predictions', methods=['POST'])
    def predict():
        content_type = request.headers[HttpHeaders.CONTENT_TYPE] if HttpHeaders.CONTENT_TYPE in request.headers \
            else None

        if not is_valid_content_type(content_type, MimeTypes.APPLICATION_JSON_PANDAS_SPLIT):
            return invalid_content_type(content_type, MimeTypes.APPLICATION_JSON_PANDAS_SPLIT)

        if not request.data:
            return bad_request_missing_body()

        try:
            request_body = request.data

            data = deserialize_dataframe(request_body)
            predictions = sagemaker_client.post_invocations(request_body)

            data_predictions = merge_predictions(data, predictions)
            sns_message_producer.publish_predictions(data_predictions)

            return make_response(jsonify(predictions), 200)
        except ValueError as err:
            return bad_request_deserialization_error(err)


if __name__ == '__main__':
    application = create_app('config.Config')
    application.run(host='0.0.0.0')
