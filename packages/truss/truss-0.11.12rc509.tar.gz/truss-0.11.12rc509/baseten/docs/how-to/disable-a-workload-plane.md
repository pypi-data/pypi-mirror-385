# How to disable a workload plane

When a workload-plane is sitting idle, brought up for testing purpose and no longer needed (in a short term), etc.
we may want to scale it down to save the cost. But we don't want the inoperable
workload-plane causes problems in our workflows or triggers unnecessary alerts.

Before we go to the UI and disable the workload-plane, we want to ensure
- No org uses that workload-plane as org level accelerator override
- Workload-plane is not the default for a GPU type
- No active models
- Deactivated models should be migrated to other workload-planes
