import json
import os
import urllib.request

LAMBDA_URL = os.environ.get(
    "LAMBDA_URL",
    "https://auwb72k75qnn3ncgrchc6qpyv40kvdaa.lambda-url.sa-east-1.on.aws/",
)


def handler(request):
    """Vercel serverless function that proxies the Lambda and adds CORS."""
    try:
        req = urllib.request.Request(LAMBDA_URL, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            status = resp.status
    except Exception as exc:  # pragma: no cover - external call
        status = 500
        body = json.dumps({"error": str(exc)})

    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": body,
    }

