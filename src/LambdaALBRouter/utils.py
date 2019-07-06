import json

def json_response(response, code=200, description="200 OK", isBase64Encoded=False, headers=None):
    response_headers = {
        "Content-Type": "application/json"
    }

    if headers and isinstance(headers, dict):
        response_headers.update(headers)

    result = {
        "statusCode": code,
        "statusDescription": description,
        "isBase64Encoded": isBase64Encoded,
        "headers": response_headers,
        "body": response
    }

    return result
