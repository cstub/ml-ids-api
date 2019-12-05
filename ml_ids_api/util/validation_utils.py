def is_valid_content_type(content_type: str, expected_content_type: str) -> bool:
    return (content_type is not None) and (content_type.strip().lower() == expected_content_type)
