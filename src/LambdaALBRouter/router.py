import inspect
import json
import re
from base64 import b64decode
from urllib.parse import parse_qs

from .exceptions import *


class ALBRouter():
    def __init__(self):
        self.routes = []

    @catch_exception
    def route(self, route_str, route_methods=None):
        def decorator(f):
            route_pattern = self.__compile_route_path(route_str)

            if isinstance(route_methods, list):
                methods = [x.lower() for x in route_methods]
            else:
                methods = []

            self.routes.append((route_pattern, methods, f))

            return f

        return decorator

    @catch_exception
    def serve(self, call_path, call_method, context=None):
        call_match = self.__find_call_match(call_path, call_method)

        if call_match:
            args, exec_function = call_match

            if "context" in inspect.signature(exec_function).parameters:
                return exec_function(**args, context=context)
            else:
                return exec_function(**args)
        else:
            raise BadGateway(f"Route {call_path} via {call_method} request has not been registered.")

    @catch_exception
    def process_lambda_alb_event(self, event):
        # Get call method
        call_method = event['httpMethod']

        # Get call path
        call_path = event['path']

        # Parse query string params
        query_string_params = event['queryStringParameters']

        # Get headers from call
        call_headers = event['headers']

        # Parse data from call
        if event['body']:
            if event['isBase64Encoded']:
                input_data = b64decode(event['body']).decode("utf-8")
                input_data = parse_qs(input_data)
                input_data = {k: v[0] for k, v in input_data.items()}
            else:
                input_data = json.loads(event['body'])
        else:
            input_data = {}

        context = Context(
            method=call_method,
            path=call_path,
            query_string=query_string_params,
            headers=call_headers,
            data=input_data
        )

        return self.serve(call_path, call_method, context)

    @staticmethod
    @catch_exception
    def __compile_route_path(route_str):
        route_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', route_str)
        return re.compile(f"^{route_regex}$")

    @catch_exception
    def __find_call_match(self, call_path, call_method):
        for route_pattern, methods, exec_function in self.routes:
            match = route_pattern.match(call_path)

            if match:
                if methods and call_method.lower() in methods:
                    return match.groupdict(), exec_function
                elif not methods:
                    return match.groupdict(), exec_function
                else:
                    continue
            else:
                continue

class Context():
    def __init__(self, method=None, path=None, query_string=None, headers=None, data=None):
        self.method = method
        self.path = path
        self.query_string = query_string
        self.headers = headers
        self.data = data
