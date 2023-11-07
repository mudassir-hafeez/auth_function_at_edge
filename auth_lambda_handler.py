import json
import boto3
import base64
import logging
import requests
from botocore.awsrequest import AWSRequest
from botocore.auth import SigV4Auth

logger = logging.getLogger(__name__)


def signed_request(event, context={}):
    logger.info("event=" + json.dumps(event))

    request = event['Records'][0]['cf']['request']
    headers = request['headers']

    # remove the x-forwarded-for from the signature
    del headers['x-forwarded-for']

    headers = {v[0]['key']: v[0]['value'] for k, v in headers.items()}

    # remove the "behaviour" path from the uri to send to Lambda
    # ex: /updateJson/234345 => /234345
    uri = request['uri'][1:]
    urisplit = uri.split('/')
    urisplit.pop(0)
    uri = '/' + '/'.join(urisplit)
    request['uri'] = uri

    host = request['headers']['host'][0]['value']
    region = host.split(".")[2]
    path = uri + ('?' + request['querystring'] if 'querystring' in request else '')

    # build the request to sign
    req = AWSRequest(
        method=request['method'],
        url=f'https://{host}{path}',
        data=base64.b64decode(request['body']['data']) if 'body' in request and 'data' in request['body'] else None,
        headers=headers
    )
    req.context['signing'] = {'signing_name': 'lambda', 'region': region}
    SigV4Auth(boto3.Session().get_credentials(), 'lambda', region).add_auth(req)

    # reformat the headers for CloudFront
    request['headers'] = {
        header.lower(): [{'key': header, 'value': value}]
        for header, value in req.headers.items()
    }
    logger.info("signedRequest=" + json.dumps(request))
    return request


def lambda_handler(event, context):
   return signed_request(event, context)


def test_lambda_handler():
    # To test lambda_handler function locally
    event = {
        "Records": [
            {
                "cf": {
                    "request": {
                        "method": "GET",
                        "uri": "/servers",
                        "headers": {
                            "host": [
                                {"key": "Host", "value": "dummyq2342fasef123424.lambda-url.us-east-1.on.aws"}
                            ],
                            "x-forwarded-for": [
                                    {"key": "X-Forwarded-For", "value": "127.0.0.1"}
                            ]
                        }
                    }
                }
            }
        ]
    }

    request = signed_request(event)
    headers = request['headers']
    data = base64.b64decode(request['body']['data']) if 'body' in request and 'data' in request['body'] else None
    url = f"https://{headers['host'][0]['value']}{request['uri']}"
    method = request['method']
    headers = {v[0]['key']: v[0]['value'] for k, v in headers.items()}
    response = requests.request(method=method, url=url, headers=headers, data=data)
    print(response.content)

if __name__ == "__main__":
    test_lambda_handler()
