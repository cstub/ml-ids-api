import os


def get_env_non_empty(key):
    value = os.environ.get(key)
    if value is None:
        raise ValueError('No value for environment variable ["{}"] supplied.'.format(key))
    return value


class Config(object):
    AWS_REGION = get_env_non_empty("AWS_REGION")
    AWS_ACCESS_KEY = get_env_non_empty("AWS_ACCESS_KEY")
    AWS_SECRET_KEY = get_env_non_empty("AWS_SECRET_KEY")
    AWS_SAGEMAKER_HOST = get_env_non_empty("AWS_SAGEMAKER_HOST")
    AWS_SAGEMAKER_ENDPOINT = get_env_non_empty("AWS_SAGEMAKER_ENDPOINT")
    AWS_SNS_PREDICTIONS_TOPIC = get_env_non_empty("AWS_SNS_PREDICTIONS_TOPIC")
