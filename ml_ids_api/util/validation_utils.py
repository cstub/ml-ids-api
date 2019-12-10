"""
Module containing utilities for request validation.
"""


def is_valid_content_type(content_type: str, expected_content_type: str) -> bool:
    """
    Checks if the given Content-Type is valid by comparing it to an expected Content-Type.

    :param content_type: Content-Type.
    :param expected_content_type: Expected Content-Type.
    :return: Binary flag whether the given Content-Type is valid.
    """
    return (content_type is not None) and (content_type.strip().lower() == expected_content_type)
