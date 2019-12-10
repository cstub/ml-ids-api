"""
Module containing utilities to create HTTP responses.
"""
from flask import make_response, jsonify


def invalid_content_type(content_type, supported_content_type):
    """
    Creates a Flask response with status code `415 - Invalid Content Type`.

    :param content_type: Content-Type.
    :param supported_content_type: Supported Content-Type.
    :return: Flask response.
    """
    return response_error(415, 'Content-Type: \'{}\' is not supported. Supported content-types are [\'{}\'].'
                          .format(content_type, supported_content_type))


def bad_request_missing_body():
    """
    Creates a Flask response with status code `400 - Client Error`, specifying that no request body was supplied.

    :return: Flask response.
    """
    return response_error(400, 'No request body supplied. Please provide a valid json request body in '
                               'Pandas \'split\' format.')


def bad_request_deserialization_error(err):
    """
    Creates a Flask response with status code `400 - Invalid Content Type`, specifying that the request body could
    not be deserialized.

    :param err: Deserialization error.
    :return: Flask response.
    """
    return response_error(400, 'Invalid request body supplied. Please provide a valid json request body in '
                               'Pandas \'split\' format. Cause: {}'.format(err))


def response_error(code: int, error_msg: str):
    """
    Creates a generic Flask response given the status code and error-message.

    :param code: Status code of the response.
    :param error_msg: Error message to be sent in the response body.
    :return: Flask response.
    """
    return make_response(jsonify({'error': error_msg}), code)
