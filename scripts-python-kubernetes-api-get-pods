from kubernetes import client, config

config.load_kube_config()
v1 = client.CoreV1Api()

pods = v1.list_pod_for_all_namespaces(watch=False)
for p in pods.items:
    print(f"{p.metadata.namespace} - {p.metadata.name} - {p.status.phase}")
