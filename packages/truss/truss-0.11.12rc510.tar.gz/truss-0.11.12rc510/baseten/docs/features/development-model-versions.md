# Development model versions

Models can have a development model version that different from other versions
in the following ways:

1. It's meant for development and has lower SLAs. e.g. it's ok for it go down
   for some time
2. It can be modified in place

Development versions are only allowed one pod and are scaled to zero quickly on
lack of use.

## Implementation

A development model version has associated patches in addition to the
OracleVersion. Client initially creates a development version and then sends
patches for it, using appropriate GraphQL mutations. Backend stores these
patches and applies them onto the running model. Applying this patches is
ultra-fast, that is the crucial benefit of development models.


### Full deployment

Similar to regular model deployments except no new versions are created,
existing version is updated. docker builds are done using tekton as usual and
inference service created or updates. Note that inference service update creates
a new revision. We may want to kill and recreate the inference service in
future.

### Patching deployment

1. Client retrieves current hash and signature
2. Computes patch and sends over
3. Backend stores the patch
4. Backend syncs the patch with running container
  * Backend retrieves current hash from running container
  * Identfies patches to apply and sends them over
  * Repeats until sync is achieved

### Model pod restart

Could be due to scaling to 0 and back, or any number of failure scenarios.

1. Model container starts up and with it the control server, but not the
   inference server.
2. Model container pings back django to apply needed patches to it
3. Backend syncs patches as in step 4 of patching deployment above
  * Inference web server is started up on sync


## Gotchas

### Truss hash

Truss's hash is embedded into the truss docker image but we override that with
an environment variable in the pod definition. This is because we apply changes
,such as adding sentry url, to the user supplied truss when we run. The built
image hash would represent these changes and hashes won't match with user
supplies truss.

Truss needs the hash in the docker image to allow for the a local dev
incremental experience outside of Baseten, so we don't want to remove that.

### Patch sync

It can take multiple retries to sync patches onto the container. User may end up
pushing many changes quickly. Another change may arrive before previous one is
applied. All these requests may go to different django pods and happen concurrently.
The check and set mechanism will make sure that patches are applied in the right order
but multiple tries may be needed.
