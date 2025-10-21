# Django application backend

Please read the [Core Product Style Guide](https://www.notion.so/ml-infra/Core-Product-Style-Guide-17e91d247273809e9c4fc76ead55a81b) before contributing

## Django gotchas

### Django model are not thread safe
Django model instances are not thread-safe. If multiple threads modify the same instance simultaneously, unexpected behavior can occur. For example, if both threads call `save()`, clobbering will occur and the object will end up with the state of the last thread that called `save()`. To workaround this, you can:
- Call `model.refresh_from_db()` to ensure you act on the latest state of the model
- Use the `update_fields` param when calling `save()` to only modify the field changed by the current operation

Examples:
- `oracles/model_deployer/deploy_model.py::deploy_model`
- `oracles/models.py::Oracle.set_primary`
