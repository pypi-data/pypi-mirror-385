## Inference Service scaling

We set the following parameters on our inference service spec with regards to scaling. These three factors control the way which inference services scale
* Max Replicas
* Min Replicas
* Parallelism

### Replicas

Minimum and Maximum replicas are straightforward. The minimum replica is the lowest number of replicas to run in the deployment. The maximum replica is the maximum replicas that are scaled to under load

### Parallelism

This factor is defined as:

> Parallelism specifies how many requests can be processed concurrently, this sets the target concurrency for Autoscaling(KPA). For model servers that support tuning parallelism will use this value, by default the parallelism is the number of the CPU cores for most of the model servers. [[source](https://github.com/kserve/kserve/blob/master/install/v0.3.0/kfserving.yaml)]

The `parallelism` parameter on an inference service corresponds to `autoscaling.knative.dev/target` in a KNative service. That is defined as  a `soft-limit` in KNative. The [soft limit](https://knative.dev/docs/serving/autoscaling/concurrency/#soft-limit) is a targeted limit. If the "average concurrency per Pod" exceeds the soft-limit by a certain rate (200% over 6s - `panic-threshold-percentage` over `stable-window`/`panic-window-percentage`, all in the `config-autoscaler` configmap in the `knative-serving` namespace). The cluster will then scale up; targeting the soft-limit parameter amongst all replicas. It is essentially the [target load]( https://knative.tips/autoscaling/target-concurrency/) in concurrent requests spread across replicas.

## Example

These two definitions come from the same deployment running a model. You can see how the parameters are set on both places. KServe is built on Knative.

```yaml
apiVersion: serving.kubeflow.org/v1alpha2
kind: InferenceService
metadata:
  name: baseten-model-v31d5r3
  namespace: baseten
spec:
  default:
    predictor:
      custom:
        container:
          image: baseten/baseten-custom-model:v31d5r3-45fc35af-49f5-42db-a81e-aaf38a878d96
          name: user-container
          ports:
          - containerPort: 8080
      maxReplicas: 3  # <--------------------
      minReplicas: 1  # <--------------------
      parallelism: 5  # <--------------------
```

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: baseten-model-v31d5r3-predictor-default
  namespace: baseten
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/class: kpa.autoscaling.knative.dev
        autoscaling.knative.dev/maxScale: "3"  # <--------------------
        autoscaling.knative.dev/minScale: "1"  # <--------------------
        autoscaling.knative.dev/target: "5"    # <--------------------
        queue.sidecar.serving.knative.dev/resourcePercentage: "20"
    spec:
      containerConcurrency: 0
      containers:
      - image: baseten/baseten-custom-model:v31d5r3-45fc35af-49f5-42db-a81e-aaf38a878d96
        name: user-container
        ports:
        - containerPort: 8080
```
