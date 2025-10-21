# How to add new fields to Api resources

As described [here](api-resources.md), Api resources are represented using
protobuf in [resources.proto](/proto/resources.proto).

To introduce a new field in a resource, update the appropriate protobuf
definition. The protobufs are automatically converted to python representation
via code generation. This conversion happens automatically during git commit,
but you may want the generated code before committing. You can run
`buf generate` from the `backend` directory for that.

With the proto definition in place you can update the export_spec method of
appropriate [Resource](/backend/workflows/api_resources/resource.py) to
make sure the newly created field is populated. If wired correctly you should
see the field in the exported yaml.

Make sure to use the field in the create method of the corresponding controller,
for it to take effect in the imported resource.
