# python-dciauth

DCI authentication module used by dci-control-server and python-dciclient

This section shows example programs written in python that illustrate how to work with Signature Version 2 in DCI. The algorithm used by dciauth is identical to [Signature Version 4 in AWS](http://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html).

## Authentication example:

Create a `HmacAuthBase` object to give to python requests module

```python
from dciauth.signature import HmacAuthBase

auth = HmacAuthBase(
    access_key="access_key",
    secret_key="secret_key",
    region="us-east-1",
    service="api",
    service_key="aws4_request",
    algorithm="AWS4-HMAC-SHA256",
)
```

GET

```python
import requests

requests.get("http://api.distributed-ci.io/api/v1/jobs", auth=auth)
```

POST

```python
import requests

requests.post("http://api.distributed-ci.io/api/v1/users", auth=auth, json={"name": "user 1"})
```

## Validation example

```python
import flask
from dciauth.signature import FlaskHmacSignature

@app.route("/api/protected", methods=["GET"])
def get_protected():
    auth_scheme = flask.request.headers.get("Authorization").split(" ")[0]
    if auth_scheme == "AWS4-HMAC-SHA256":
        signature = FlaskHmacSignature(
            {
                "service_name": "api",
                "service_key": "aws4_request",
                "region_name": "us-east-1",
                "algorithm": "AWS4-HMAC-SHA256",
            }
        ).add_request(flask.request)
        assert signature.access_key == "access_key"
        if not signature.is_valid(secret_key="secret_key"):
            return "ko", 401
        return "ok", 200
    return "ko", 400
```

## Using POSTMAN

If you are using POSTMAN to discover DCI API you can use the following parameters with the AWS Signature authorization header:

    GET https://api.distributed-ci.io/api/v1/identity
    AccessKey=<DCI_CLIENT_ID>
    SecretKey=<DCI_API_SECRET>
    AWS Region="BHS3"
    Service Name="api"

## License

Apache 2.0

## Author Information

Distributed-CI Team <distributed-ci@redhat.com>
