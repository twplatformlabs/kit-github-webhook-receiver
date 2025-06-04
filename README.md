<div align="center">
	<p>
		<img alt="Thoughtworks Logo" src="https://raw.githubusercontent.com/twplatformlabs/static/master/psk_banner.png" width=800 />
	</p>
  <h3>kit-github-webhook-receiver</h3>
  <h5>API Starterkit for receiving GitHub webhook events</h5>
  <a href="https://dl.circleci.com/status-badge/redirect/gh/twplatformlabs/kit-github-webhook-receiver/tree/main"><img src="https://dl.circleci.com/status-badge/img/gh/twplatformlabs/kit-github-webhook-receiver/tree/main.svg?style=svg"></a> <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/license-MIT-blue.svg"></a> <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</div>
<br />

# GitHub Webhook Receiver (FastAPI Template)

A minimal, secure, and extensible [FastAPI](https://fastapi.tiangolo.com/) service that receives and processes GitHub webhook events.

This project provides a clean and modular template for building GitHub webhook integrations using FastAPI, with basic security, observability, and customization points.

## Features

* **Secure signature verification** using `X-Hub-Signature-256` and HMAC.
* **Request payload size limiting** with customizable middleware.
* **Modular design**: plug in your own handlers for GitHub events via `actions.py`.
* **OpenTelemetry tracing support** for enhanced observability.

## Configuration

### Ingress

Sample Helm deployment demonstrates a typically Istio managed ingress pattern and the use of a VirtualService. Always deploy behind HTTPS.  

### Required Environment Variables

| Variable         | Description                                                                                        | Default            |
| ---------------- | -------------------------------------------------------------------------------------------------- | ------------------ |
| `WEBHOOK_SECRET` | **Shared secret** Configured in your GitHub webhook settings. Required for signature verification. | `"secret_not_set"` |
| `API_VERSION`    | Optional release identifier (e.g., `v1.2.0`) shown in health checks and apidocs.                   | `"snapshot"`  

#### Securing Webhooks with `WEBHOOK_SECRET`

GitHub signs each webhook payload it sends using a secret you define. This app verifies the `X-Hub-Signature-256` using your configured `WEBHOOK_SECRET`.

##### Steps:

1. Deployed as Kubernetes secret:  

Example generates values template at deploy time.  

```yaml
echo "set webhook-secret-value.yaml"
op inject -i tpl/webhook-secret-value.yaml.tpl -o charts/github-webhook-receiver/webhook-secret-value.yaml

echo "deploy github-webhook-receiver:$tag to demo-$env"
helm upgrade github-webhook-receiver charts/github-webhook-receiver \
      --install --atomic --timeout 120s \
      --namespace "demo-$env" \
      --values "charts/github-webhook-receiver/values.yaml" \
      --values "charts/github-webhook-receiver/values-$env.yaml" \
      --values "charts/github-webhook-receiver/webhook-secret-value.yaml" \
      --set image.tag="$tag"
```

2. Service will reject any webhook requests that:

   * Have an invalid signature
   * Payload signature hash does not match payload
   * Exceed the payload size limit (default: 2MB)

### Customizing Event Handlers

The main route handler (in api/main.py) will dispatch processing based on the type of webhok event received. There are several example event types shown in the comments section.  
```python
    # Process the webhook payload for supported response options
    match payload:
        case {"ref": _, **_rest} if "ref_type" not in payload:
            on_push(payload)

        # Implement handlers for other GitHub events as needed
        # case {"action": "opened", "pull_request": _, **_rest}:
        #     on_pull_request(payload)
        # case {"action": "opened", "issue": _, **_rest}:
        #     on_issue_create(payload)
        # case {"ref": _, "ref_type": _, **_rest}:
        #     on_tag(payload)
        # case {"action": "created", "repository": _, **_rest}:
        #     on_repository_create(payload)
```
Add custom handlers to actions.py or define your own structure around your specific use case.  

### Observability

* OpenTelemetry FastAPI instrumentation is automatically enabled. Add traces to your custom event handlers for enhanced observability.
* Endpoint: `GET /v1/webhook/healthz` functionally provides only simple liveness check. Response includes status, version info, and current UTC time. Add readiness route based on custom handler actions.
* Add operational dashboards, monitors, and alerts using your own standard observability tooling.


## 🧪 Development

### Requirements

* Python 3.10+
* [uvicorn](https://www.uvicorn.org/) for local dev server

#### local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt requirements-dev.txt
```

**run locally with uvicorn**  

```bash
export WEBHOOK_SECRET="supersecret123"
uvicorn api.main:api --reload
```

**confirm health**  
```bash
curl http://localhost:8000/v1/webhook/healthz
{"status":"ok","api":"v1","version":"snapshot","description":"github webhook receiver","time (UTC)":"2025-00-00T00:00:00.00000+00:00"}
```

### Example Postman setup for POST http://localhost:8000/v1/webhook

Paste a sample payload in the body tab:  
```json
{
  "ref": "refs/heads/main",
  "repository": {
    "full_name": "example/repo"
  },
  "pusher": {
    "name": "test-user"
  }
}
```
The header section will require a HMAC hash of this payload using the secret. You can use an online hash generator (be careful not to use a secret that will be used on publically accessable service deployments), or you could use a simple python script like:
```python
import hmac
import hashlib

secret = b"supersecret123"
with open("payload.json", "rb") as f:
    body = f.read()

sig = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()
print(sig)
```
Results in an output similar to:  
```bash
sha256=de2c8f1425f7337a9f19b7c55d93e8c672302b8d8a1d9f2
```
Once you have the hash version of the payload, add an entry on the headers tab:  
`X-Hub-Signature-256: sha256=de2c8f1425f7337a9f19b7c55d93e8c672302b8d8a1d9f2`  

Now, hit SEND. If correctly setup you will receive a 200 response.  
```json
{
    "message": "Webhook received successfully"
}
```
### Healthy pod log messages

A typically log stream for a healthy webhook, and with a GitHub push event being received, will look like this:  
```bash
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.6:34153 - "GET /v1/webhook/healthz HTTP/1.1" 200 OK
INFO:     127.0.0.6:53927 - "GET /v1/webhook/healthz HTTP/1.1" 200 OK
INFO:     127.0.0.6:49329 - "GET /v1/webhook/healthz HTTP/1.1" 200 OK
INFO:     127.0.0.6:58999 - "GET /v1/webhook/healthz HTTP/1.1" 200 OK
INFO:     127.0.0.6:54267 - "GET /v1/webhook/healthz HTTP/1.1" 200 OK
INFO:     127.0.0.6:43137 - "GET /v1/webhook/healthz HTTP/1.1" 200 OK
INFO:     127.0.0.6:52509 - "GET /v1/webhook/healthz HTTP/1.1" 200 OK
Push event data: {'ref': 'refs/heads/main', 'before': '1095f728d68b83773fe1fd249ea', 'after': '2edac7051c3c669b039783', 'repository': {'id': 996190...
INFO:     127.0.0.6:45841 - "POST /v1/webhook HTTP/1.1" 202 Accepted
```