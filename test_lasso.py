import subprocess
import time
import re

import pytest


KUBE_YAML = "microservices-demo/release/kubernetes-manifests.yaml"
NAMESPACE = "pytest-lasso"
SETUP_TIMEOUT = 100


def create_namespace():
    """Creates namespace if it doesn't already exist"""
    cli_output = subprocess.run([
        "minikube", "kubectl", "--",
        "get", "namespace"
        ], stdout=subprocess.PIPE)
    cli_output_str = cli_output.stdout.decode("utf-8")
    namespaces = [ln.split(" ")[0] for ln in cli_output_str.split("\n")[1:-1]]
    if NAMESPACE not in namespaces:
        subprocess.run([
            "minikube", "kubectl", "--",
            "create", "namespace", NAMESPACE
            ])


def wait_until_resources_ready():
    """Waits until resources ready in desired namespace"""
    start = time.time()
    while True:
        pods_ready = True
        cli_output = subprocess.run([
            "minikube", "kubectl", "--",
            "get", "pods", "-n", NAMESPACE
            ], stdout=subprocess.PIPE)
        cli_output_str = cli_output.stdout.decode("utf-8")
        lines = cli_output_str.split("\n")[1:-1]
        for line in lines:
            pod_info = re.split(r'\s{2,}', line)
            ready = pod_info[1]
            if ready != "1/1":
                pods_ready = False
        if pods_ready:
            break
        elif time.time() - start > SETUP_TIMEOUT:
            subprocess.run([
                "minikube", "kubectl", "--",
                "delete",
                "-f", KUBE_YAML,
                "-n", NAMESPACE
                ])
            raise TimeoutError("Took too long to setup resources")
        time.sleep(0.5)


@pytest.fixture(autouse=True)
def setup_and_teardown_resources():
    create_namespace()
    subprocess.run([
        "minikube", "kubectl", "--",
        "apply",
        "-f", KUBE_YAML,
        "-n", NAMESPACE
        ])
    wait_until_resources_ready()
    yield None
    subprocess.run([
        "minikube", "kubectl", "--",
        "delete",
        "-f", KUBE_YAML,
        "-n", NAMESPACE
        ])


def test_k8s():
    assert True
