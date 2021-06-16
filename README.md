# global-image-puller

This is a very rudimentary Kubernetes Controller that will watch for namespace creation and create a image-puller rolebinding for that namespace in the `system-images` namespace. It will delete that rolebinding on namespace deletion.

## Demo

1. Run the controller locally

    ```
    ./global-image-puller.py
    ```

1. Create a namespace (or openshift project)

    ```
    kubectl create ns project-a
    ```

1. Check for a role binding in `system-images`

    ```
    kubectl -n system-images get rolebinding image-puller-project-a
    ```