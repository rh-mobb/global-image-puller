import json
import yaml
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
import os

def main():
    if 'KUBERNETES_PORT' in os.environ:
        config.load_incluster_config()
    else:
        config.load_kube_config()
    configuration = client.Configuration()
    configuration.assert_hostname = False
    # api_client = client.api_client.ApiClient(configuration=configuration)
    v1 = client.CoreV1Api()
    rbac_v1 = client.RbacAuthorizationV1Api()

    while True:
        stream = watch.Watch().stream(v1.list_namespace)
        for event in stream:
            operation = event['type']
            metadata = event['object'].metadata
            name = metadata.name
            annotations = metadata.annotations
            crb_name = "system:image-puller-{0}".format(name)
            if name.startswith("openshift"):
                continue
            if "openshift.io/requester" in annotations:
                if operation == "DELETED":
                    print("namespace %s was deleted" % name)
                    try:
                        print("deleting rolebinding for %s" % name )
                        rbac_v1.delete_namespaced_role_binding(crb_name, "system-images")
                    except ApiException as e:
                        if e.status == 404:
                            continue
                        else:
                            print("Exception when calling RbacAuthorizationV1Api->read_cluster_role_binding: %s\n" % e)
                            continue
                if operation == "ADDED":
                    print("namespace %s was added" % name)
                    # body = client.V1ClusterRoleBinding()
                    body = yaml.safe_load(f"""
                    apiVersion: rbac.authorization.k8s.io/v1
                    kind: RoleBinding
                    metadata:
                      name: {crb_name}
                    roleRef:
                      apiGroup: rbac.authorization.k8s.io
                      kind: ClusterRole
                      name: system:image-puller
                    subjects:
                    - kind: ServiceAccount
                      name: default
                      namespace: {name}
                    """)
                    try:
                        crb = rbac_v1.read_namespaced_role_binding(crb_name, "system-images")
                        # pprint(api_response)
                    except ApiException as e:
                        if e.status == 404:
                            print("Creating rolebinding for {}".format(name))
                            rbac_v1.create_namespaced_role_binding("system-images", body)
                            continue
                        else:
                            print("Exception when calling RbacAuthorizationV1Api->read_cluster_role_binding: %s\n" % e)
                            continue


if __name__ == "__main__":
    main()