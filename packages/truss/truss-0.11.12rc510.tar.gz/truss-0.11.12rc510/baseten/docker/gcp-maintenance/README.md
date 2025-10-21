# Interactively migrate models and change instance group size back
When GCP put a maintenance event on a node, we need to migrate the models running on the node, delete, and create a new node.

## Setup and run
- Apply the `example-pod.yaml` manifest to the cluster. Change the pod name (`metadata.name`) if you need to run multiple pods at the same time. 

  `kubectl apply -f example-pod.yaml`
- Get a shell on the pod
  
  ```
  kubectl -n baseten exec -it gcp-maintenance-pod -- bash
  ## optionally install ipython
  pip install ipython
  ```

- Set the environment variables from the shell
  ```
  export ALERT_LABEL_INSTANCE_NAME=<instance-name-needs-to-be-deleted>

  ## Following are set to True by default, change as needed
  ## Do not set those to True unless you need to do something else.
  # set to False to just migrate the pods, leave node cordoned
  TERMINATE_INSTANCE=False
  # do not resize the instance group after terminate the instance
  RESIZE_IG=False
  # do not wait for the new node to be ready and label/taint it
  WAIT_NEW_NODE=False
  ```

- Run python script `python3 /gcp_maintenance.py`

## Cleanup
The pod will run for 1 hour and then complete. If you need more time, echo the number of seconds into `/tmp/more_sleep`. For example `echo 3600 > /tmp/more_sleep` will extend the pod's life by 1 hour. This can only be done once.


