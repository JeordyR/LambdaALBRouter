"""
LambdaAlbRouter.router

Implements the central ALBRouter and Context objects for processing requests and storing data.
"""

# Standard imports
import inspect
import json
import logging
import re
from base64 import b64decode
from urllib.parse import parse_qs

# Local imports
from .exceptions import *

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ALBRouter():
    """
    The ALBRouter object acts as the central routing object. It registers a list of routes and processes
    incoming lambda events to trigger the associated route. It is designed to not store any run-time data
    so it can be used as a global object allowing it to be cached between lambda executions without running
    into any data cacheing issues between executions.

    Usage:
        from LambdaALBRouter import router
        app = router.ALBRouter()
    """
    def __init__(self):
        self.routes = []

    @catch_exception
    def route(self, route_str: str, route_methods: list = None):
        """
        Decorator that registers execution functions for a URL path.
        Usage:
            @app.route('/', methods=['GET'])
            def hello():
                ...

        :param route_str: The URL path to register for this router
        :param route_methods: List of methods that the route supports, will default to all if not specified
        """
        def decorator(f):
            # Compile the route_str into a regex object
            route_pattern = self.__compile_route_path(route_str)

            # Parse the method(s) into a list
            if isinstance(route_methods, list):
                methods = [x.lower() for x in route_methods]
            elif isinstance(route_methods, str) and route_methods:
                methods = [methods.lower()]
            else:
                methods = []

            # Store the processed route
            self.routes.append((route_pattern, methods, f))

            logger.debug(f"Registered route: {route_str} with method(s): {route_methods}")

            return f

        return decorator

    @catch_exception
    def serve(self, call_path: str, call_method: str, context: object = None) -> dict:
        """
        Function that finds a match to the call details provided and executes the discovered exec function.
        If no matching route is found for the call it raises an exception which is handled by the catch_exception
        dectorator and turned into BadGateway response to the ALB.

        :param call_path: URL path of the triggering call
        :param call_method: Method of the triggering call
        :param context: Context object containing input data if present
        :return: Returns the response from the exec function
        """
        logger.info(f"Looking for route matching call: {call_path}({call_method})")

        # Look for a registered route matching the call details
        call_match = self.__find_call_match(call_path, call_method)
        logger.debug(f"Found matching call: {call_match}")

        if call_match:
            args, exec_function = call_match

            # Check if the exec function is expecting the Context object and pass it if so
            if "context" in inspect.signature(exec_function).parameters:
                logger.debug(f"Executing function: {exec_function.__name__} with args: {args}, and passing context")
                return exec_function(**args, context=context)
            else:
                logger.debug(f"Executing function: {exec_function.__name__} with args: {args}")
                return exec_function(**args)
        else:
            raise NotFound(f"Route {call_path} via {call_method} request has not been registered.")

    @catch_exception
    def process_lambda_alb_event(self, event: dict) -> dict:
        """
        Function that takes in an AWS Lambda event triggered by an Application Load Balancer, parses out the
        required fields and user input, then calls the serve function to handle the execution.

        The body of POST requests, if encoded, is decoded and passed through. All data is stored in a new Context
        object and passed through the functions instead of being stored in the ALBRouter instance to avoid
        cacheing issues between Lambda executions.

        :param event: The ALB triggered lambda event
        :return: Returns the response from self.serve, which is the response from the exec function
        """
        logger.info(f"Processing event: {event}")
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

        logger.debug("Parsed parameters:")
        logger.debug(f"call_method: {call_method}")
        logger.debug(f"call_path: {call_path}")
        logger.debug(f"query_string_params: {query_string_params}")
        logger.debug(f"call_headers: {call_headers}")
        logger.debug(f"input_data: {input_data}")


        # Generate a Context object with the parsed data
        logger.debug("Generating context object with parsed parameters.")
        context = Context(
            method=call_method,
            path=call_path,
            query_string=query_string_params,
            headers=call_headers,
            data=input_data
        )

        # Call serve passing the parsed values and return the result
        return self.serve(call_path, call_method, context)

    @staticmethod
    @catch_exception
    def __compile_route_path(route_str: str) -> object:
        """
        Compiles the route_str into a regex object that can parse fields from the path.

        :param route_str: The URL path to register for this router
        :return: Compiled regex match string
        """
        route_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', route_str)
        return re.compile(f"^{route_regex}$")

    @catch_exception
    def __find_call_match(self, call_path: str, call_method: str) -> (dict, object):
        """
        Finds a matching registered route based on the calls path and method.

        :param call_path: URL path in the calling event
        :param call_method: Method of the call (GET, POST, etc.)
        """
        # Loops through all registered routes, checking for match on the call params
        for route_pattern, methods, exec_function in self.routes:
            match = route_pattern.match(call_path)

            if match:
                logger.debug(f"Found potential match: {match}")
                if methods and call_method.lower() in methods:
                    logger.debug(f"Returning match: {match}")
                    return match.groupdict(), exec_function
                elif not methods:
                    logger.debug(f"Returning match: {match}")
                    return match.groupdict(), exec_function
                else:
                    logger.debug(f"Call method {call_method} does not match {match}, continuing to search.")
                    continue
            else:
                continue

class Context():
    """
    The Context object acts as the primary method of runtime data storage. Object instances are instantiated
    on execution of process_lambda_alb_event allowing the runtime data to remain unique between executions while
    the ALBRouter instance can be kept globally between lambda executions.

    Stores the useful enformation from the calling lambda event.

    :param method: Method of the calling request (GET, POST, etc.)
    :param path: URL path of the calling request
    :param query_string: Query string, if present, from the event
    :param headers: All of the request headers from the calling event
    :param data: Parsed data from the request (body field from the event)
    """
    def __init__(self, method=None, path=None, query_string=None, headers=None, data=None):
        self.method = method
        self.path = path
        self.query_string = query_string
        self.headers = headers
        self.data = data
