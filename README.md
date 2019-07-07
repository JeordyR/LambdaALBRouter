# LambdaALBRouter

LambdaALBRouter is a small package with flask-like syntax for routing requests from an AWS ALB in Lambda. It parses out all relavent information from the triggering event and passes it through to a matching registered route. With exceptions handled and turned into json responses, utilities for quickly exiting and returning json it is very easy to make quick APIs with ALB-fronted Lambdas in AWS.

Currently there is nothing implemented for handling templates or returning HTML, but that will be added in the future. Runtime data is stored in a separate class and not stored in the instance of ALBRouter to allow that instance to be a global variable (and cached between lambda executions) without running into caching issues.

## Installing

`pip install -U LambdaALBRouter`


## Example

```
from LambdaALBRouter import router, abort, response

app = router.ALBRouter()

def lambda_handler(event, _context):
    return app.process_lambda_alb_event(event)

@app.route("/")
def hello():
    return response("Hello world!")

@app.route("/hello/<user>")
def hello_user(user):
    return response(f"Hello {user}!")

@app.route("/update/<user>", route_methods=["POST"])
def update_user(user, context):
    input_data = context.data
    query_string = context.query_string
    request_headers = context.request_headers

    if not "something" in input_data.keys():
        abort(400, "Missing required input 'something'")

    # Update user in a database...

    return response(
        {
            "message": f"Updated {user}!",
            "context": context.__dict__
        }
    )
```
