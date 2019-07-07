"""
LambdaALBRouter.utils

Implements various utilities to help with input/output processing.
"""

import logging

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def response(
        response_body,
        code: int = 200,
        description: str = "200 OK",
        is_base64_encoded: bool = False,
        headers: dict = None
    ) -> dict:
    """
    Formats a dictionary response with the fields required for ALB allowing optional overrides of the values.
    Note for JSON responses that the ALB will handle the JSON serialization,
        this intentionally returns a dict, not a JSON string.

    :param response_body: Main body of the response, can be any type but should be JSON serializable
    :param code: HTTP status code of the response, defaults to 200
    :param description: Description of the HTTP status code
    :param is_base64_encoded: Boolean flag noting whether the response_body is Base64 encoded or not
    :param headers: Set of headers to include in the response. Can be used to override the Content-Type
    :return: Dictionary formatted with all of the required fields for ALB
    """
    logger.info(f"Generating a standard ALB response with body: {response_body} and code: {code}")

    response_headers = {
        "Content-Type": "application/json"
    }

    if headers and isinstance(headers, dict):
        response_headers.update(headers)

    result = {
        "statusCode": code,
        "statusDescription": description,
        "isBase64Encoded": is_base64_encoded,
        "headers": response_headers,
        "body": response_body
    }

    logger.debug(f"Generated response: {result}")

    return result
