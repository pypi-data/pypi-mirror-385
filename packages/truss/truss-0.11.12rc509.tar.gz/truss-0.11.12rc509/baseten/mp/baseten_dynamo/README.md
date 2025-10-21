# Baseten Dynamo

We want to support a number of model serving optimizations via NVIDIA Dynamo. To
begin with, we'll support kv cache aware routing. Disaggregated serving support
and kv cache management support will be added later.

This project is where we'll keep Dynamo service code for all of the above.
Please see cache_aware_routing for the kv cache aware routing deployment on
Dynamo.