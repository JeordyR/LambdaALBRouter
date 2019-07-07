import json
import sys
import unittest

sys.path.append("..")

from src.LambdaALBRouter import router, abort, response

app = router.ALBRouter()

def lambda_handler(event):
    return app.process_lambda_alb_event(event)


@app.route("/")
def hello():
    return response("Hello!")


@app.route("/hello/<user>")
def hello_user(user):
    return response(f"Hello {user}!")


@app.route("/update/<user>", route_methods=["POST"])
def update_user(user, context):
    return response(
        {
            "message": f"Updated {user}!",
            "context": context.__dict__
        }
    )


class TestLambdaALBRouter(unittest.TestCase):

    def setUp(self):
        event = {}

    def test_valid_get_request_root(self):
        event = {
            "requestContext": {
                "elb": {
                    "targetGroupArn": "arn:"
                }
            },
            "httpMethod": "GET",
            "path": "/",
            "queryStringParameters": {},
            "headers": {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate",
                "accept-language": "en-us",
                "connection": "keep-alive",
                "content-length": "226",
                "content-type": "application/json",
                "host": "dummyhost.dummy.com",
                "user-agent": "Rested/2009 CFNetwork/902.1 Darwin/17.7.0 (x86_64)",
                "x-amzn-trace-id": "Root=1-xxxxx-xxxxxxxxxxxxxx",
                "x-forwarded-for": "1.1.1.1",
                "x-forwarded-port": "443",
                "x-forwarded-proto": "https"
            },
            "body": "",
            "isBase64Encoded": False
        }

        result = lambda_handler(event)
        self.assertEqual(200, result['statusCode'])
        self.assertEqual("Hello!", result['body'])

    def test_valid_get_request_with_user(self):
        event = {
            "requestContext": {
                "elb": {
                    "targetGroupArn": "arn:"
                }
            },
            "httpMethod": "GET",
            "path": "/hello/user",
            "queryStringParameters": {},
            "headers": {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate",
                "accept-language": "en-us",
                "connection": "keep-alive",
                "content-length": "226",
                "content-type": "application/json",
                "host": "dummyhost.dummy.com",
                "user-agent": "Rested/2009 CFNetwork/902.1 Darwin/17.7.0 (x86_64)",
                "x-amzn-trace-id": "Root=1-xxxxx-xxxxxxxxxxxxxx",
                "x-forwarded-for": "1.1.1.1",
                "x-forwarded-port": "443",
                "x-forwarded-proto": "https"
            },
            "body": "",
            "isBase64Encoded": False
        }

        result = lambda_handler(event)
        self.assertEqual(200, result['statusCode'])
        self.assertEqual("Hello user!", result['body'])

    def test_valid_post_request_with_data(self):
        event = {
            "requestContext": {
                "elb": {
                    "targetGroupArn": "arn:"
                }
            },
            "httpMethod": "POST",
            "path": "/update/user",
            "queryStringParameters": {},
            "headers": {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate",
                "accept-language": "en-us",
                "connection": "keep-alive",
                "content-length": "226",
                "content-type": "application/json",
                "host": "dummyhost.dummy.com",
                "user-agent": "Rested/2009 CFNetwork/902.1 Darwin/17.7.0 (x86_64)",
                "x-amzn-trace-id": "Root=1-xxxxx-xxxxxxxxxxxxxx",
                "x-forwarded-for": "1.1.1.1",
                "x-forwarded-port": "443",
                "x-forwarded-proto": "https"
            },
            "body": "{\n  \"first_name\": \"Bob\",\n  \"last_name\": \"Smith\"\n}",
            "isBase64Encoded": False
        }

        result = lambda_handler(event)
        self.assertEqual(200, result['statusCode'])
        self.assertEqual("Updated user!", result['body']['message'])
        self.assertEqual("Bob", result['body']['context']['data']['first_name'])
        self.assertEqual("Smith", result['body']['context']['data']['last_name'])

    def test_invalid_path(self):
        event = {
            "requestContext": {
                "elb": {
                    "targetGroupArn": "arn:"
                }
            },
            "httpMethod": "POST",
            "path": "/thing/doesnotexist",
            "queryStringParameters": {},
            "headers": {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate",
                "accept-language": "en-us",
                "connection": "keep-alive",
                "content-length": "226",
                "content-type": "application/json",
                "host": "dummyhost.dummy.com",
                "user-agent": "Rested/2009 CFNetwork/902.1 Darwin/17.7.0 (x86_64)",
                "x-amzn-trace-id": "Root=1-xxxxx-xxxxxxxxxxxxxx",
                "x-forwarded-for": "1.1.1.1",
                "x-forwarded-port": "443",
                "x-forwarded-proto": "https"
            },
            "body": "",
            "isBase64Encoded": False
        }

        result = lambda_handler(event)
        self.assertEqual(404, result['statusCode'])

    def test_get_request_to_post_only_endpoint(self):
        event = {
            "requestContext": {
                "elb": {
                    "targetGroupArn": "arn:"
                }
            },
            "httpMethod": "GET",
            "path": "/update/user",
            "queryStringParameters": {},
            "headers": {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate",
                "accept-language": "en-us",
                "connection": "keep-alive",
                "content-length": "226",
                "content-type": "application/json",
                "host": "dummyhost.dummy.com",
                "user-agent": "Rested/2009 CFNetwork/902.1 Darwin/17.7.0 (x86_64)",
                "x-amzn-trace-id": "Root=1-xxxxx-xxxxxxxxxxxxxx",
                "x-forwarded-for": "1.1.1.1",
                "x-forwarded-port": "443",
                "x-forwarded-proto": "https"
            },
            "body": "",
            "isBase64Encoded": False
        }

        result = lambda_handler(event)
        self.assertEqual(404, result['statusCode'])


if __name__ == "__main__":
    unittest.main()
