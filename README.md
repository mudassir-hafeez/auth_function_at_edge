# AuthFunctionAtEdge

## Introduction
Lambda function to be executed at Lambda@Edge.


## Testing

To test lambda function locally, please clone the repo.

After cloning, go to the repository and then type the following commands to create a virtual environment to install dependencies and activate it:

```sh
$ cd auth_function_at_edge 
$ python3 -m venv venv
$ source venv/bin/activate
```

```bash

(venv)$ pip3 install -r requirements.txt

```

Test lambda function by running auth_lambda_handler.py, but before that set your AWS credentials as environment 
variables.

```bash
$ export AWS_ACCESS_KEY_ID=""
$ export AWS_SECRET_ACCESS_KEY="" 
$ export AWS_SESSION_TOKEN=""
```
