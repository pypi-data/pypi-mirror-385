## Tekton

We use [Tekton](https://tekton.dev/) as a tool for pipelines that execute inside of our Kubernetes cluster

### Recommended Approach

We have an interface that supports YAML files as well as a reflected objects from  the CRD definitions. 

It is highly recommended to define as much of the pipeline as possible in YAML files. Most `Tasks` should be static, defined as YAML, and managed via helm. Reference the [PyNode build task](/helm/charts/baseten-tekton/templates/build_from_s3_task.yaml) as an implementation that does this well. 

For the artifacts that run build tasks such as `PipelineRun` or `TaskRun`, the recommended approach is to start with the definition of the schema of the object (e.g. `V1beta1PipelineRun`) and work your way back with the schemas
