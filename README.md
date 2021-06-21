# global-image-puller

This is a very rudimentary OpenShift (Kubernetes) Controller that will watch for namespace creation and create a image-puller rolebinding for that namespace in the `common-images` namespace. It will delete that rolebinding on namespace deletion.

OpenShift uses cluster authorization to protect images that are built in a particular namespace from being accessed by other namespaces. This Controller allows you to create a shared images namespace that you can build images for that can be accessible by any namespace.

Minor modification would allow you to provide namespaces, namespace-prefix, maybe even user specific (as OpenShift lists the owner of new namespaces in annotations) rules on what should have access to public images.

This is meant to demonstrate how to write a simple controller in Python, and is not intended to be used in production. The more appropriate way to solve this problem is with policies. For example this pair of commands would make images in a namespace available to *any* authenticated user:

```
oc adm policy add-cluster-role-to-group system:image-puller \
  system:authenticated --namespace=common-images

oc adm policy add-role-to-group view system:authenticated -n common-images
```


## Demo

1. Run the controller locally

    ```
    ./global-image-puller.py
    ```

1. Create a namespace (or openshift project)

    ```
    kubectl create ns project-a
    ```

1. Check for a role binding in `common-images`

    ```
    kubectl -n common-images get rolebinding image-puller-project-a
    ```


## Deploy

```
oc new-project common-images

oc new-app https://github.com/openshift/ruby-hello-world.git#beta4

IMAGE=`oc get deployment ruby-hello-world -o json | jq '.spec.template.spec.containers[0].image'`

echo $IMAGE

oc adm policy add-cluster-role-to-group system:image-puller \
  system:authenticated --namespace=common-images
oc adm policy add-role-to-group view system:authenticated -n common-images

oc new-project my-app

oc create deployment my-app --image=$IMAGE
```

verify

```
oc get pods
```

output

```
NAME                      READY   STATUS    RESTARTS   AGE
my-app-6566b99587-qqfwt   1/1     Running   0          16s
```


