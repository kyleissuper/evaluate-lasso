import subprocess
import time
import re

import pytest

import config


def create_namespace():
    """Creates namespace if it doesn't already exist"""
    cli_output = subprocess.run([
        "minikube", "kubectl", "--",
        "get", "namespace"
        ], stdout=subprocess.PIPE)
    cli_output_str = cli_output.stdout.decode("utf-8")
    namespaces = [ln.split(" ")[0] for ln in cli_output_str.split("\n")[1:-1]]
    if config.NAMESPACE not in namespaces:
        subprocess.run([
            "minikube", "kubectl", "--",
            "create", "namespace", config.NAMESPACE
            ])


def expose_frontend() -> tuple[subprocess.Popen, str]:
    """Exposes frontend service; returns process, base URL"""
    process = subprocess.Popen(
            [
                "minikube", "service", "frontend",
                "-n", config.NAMESPACE,
                "--url"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
            )
    while True:
        line = process.stdout.readline().strip()
        if line[:4] == "http":
            return process, line


def wait_until_resources_ready():
    """Waits until resources ready in desired namespace"""
    start = time.time()
    while True:
        pods_ready = True
        cli_output = subprocess.run([
            "minikube", "kubectl", "--",
            "get", "pods", "-n", config.NAMESPACE
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
        elif time.time() - start > config.SETUP_TIMEOUT:
            subprocess.run([
                "minikube", "kubectl", "--",
                "delete",
                "-f", config.KUBE_YAML,
                "-n", config.NAMESPACE
                ])
            raise TimeoutError("Took too long to setup resources")
        time.sleep(0.5)


@pytest.fixture
def base_url() -> str:
    """Set up microservices, yield base_url, teardown after test"""
    create_namespace()
    subprocess.run([
        "minikube", "kubectl", "--",
        "apply",
        "-f", config.KUBE_YAML,
        "-n", config.NAMESPACE
        ])
    wait_until_resources_ready()
    frontend_process, frontend_base_url = expose_frontend()
    yield frontend_base_url
    frontend_process.kill()
    subprocess.run([
        "minikube", "kubectl", "--",
        "delete",
        "-f", config.KUBE_YAML,
        "-n", config.NAMESPACE
        ])
