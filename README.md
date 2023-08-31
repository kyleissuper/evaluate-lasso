This boilerplate code runs GCP's microservices demo in Kubernetes locally using minikube, enabling us to write a test suite that covers unit tests, integration tests, and system tests.

For example, we could write some tests like this in any `test_*.py` file, and then run `pytest`:

```python
import subprocess

import requests

from fixture_setup import base_url
import config


#  When `base_url` is set as a test function argument,
#  `fixture_setup` automatically spins up a kubernetes
#  environment, and tears it down after use.
#  It can be configured to run per test case, or per
#  test session.
def test_get_homepage(base_url):
    r = requests.get(base_url)
    assert r.status_code == 200


#  For more thorough system testing, we might expect
#  that the system gracefully handles microservice
#  failures, like redis going down. So let's do that!
def test_kill_redis(base_url):
    subprocess.run([
        "minikube", "kubectl", "--",
        "scale", "deployment/redis-cart",
        "--replicas=0",
        "-n", config.NAMESPACE
        ])
    time.sleep(5)
    r = requests.get(base_url)
    assert r.status_code == 200
```

### Requirements
- python requirements: `requirements.txt`
- assumes `minikube` is installed

### How to use
Run `pytest`
