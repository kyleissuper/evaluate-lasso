import subprocess
import time

import requests

from fixture_setup import base_url  # noqa: F401
import config


def test_kill_redis(base_url):  # noqa: F811
    subprocess.run([
        "minikube", "kubectl", "--",
        "scale", "deployment/redis-cart",
        "--replicas=0",
        "-n", config.NAMESPACE
        ])
    time.sleep(5)
    r = requests.get(base_url)
    assert r.status_code == 200
