from flask import make_response, jsonify


def invalid_content_type(content_type, supported_content_type):
    return response_error(415, 'Content-Type: \'{}\' is not supported. Supported content-types are [\'{}\'].'
                          .format(content_type, supported_content_type))


def bad_request_missing_body():
    return response_error(400, 'No request body supplied. Please provide a valid json request body in '
                               'Pandas \'split\' format.')


def bad_request_deserialization_error(err):
    return response_error(400, 'Invalid request body supplied. Please provide a valid json request body in '
                               'Pandas \'split\' format. Cause: {}'.format(err))


def response_error(code: int, error_msg: str):
    return make_response(jsonify({'error': error_msg}), code)
