# MCS Managing Resource State
MCS consists of two services: Autoscaler and Scheduler.
Both services share the same framework in managing resource state. This framework is similar to how the way k8s informers work.

MCS keeps all the required resources' state in memory caches. Autoscaler and Scheduler core logic depend directly only on the caches for read operations. The only interaction with the database is when it needs to make changes to the resource it has ownership of e.g. Autoscaler is responsible for DeploymentScale, and Scheduler is responsible for DeploymentSchedule.

On startup, we capture the latest kafka offsets from the GNS resource topics. This will ensure that we will not miss any change events after we read the full state from the database. The memory cache (ResourceCache) is then initialize with the latest full state of the resource (from database). After that point, we will start reading
the GNS change events for notification (ResourceChangeConsumer) from the earlier captured offsets. When a change event is received for a specific resource object (id), the reconciler (ResourceReconciler) will go directly to the database to found the latest state of this resource object. By comparing this latest state with what's in the cache, it can deduce whether this is a add/update/delete. It will update the cache
to keep it in sync with the database, and it will call the registered event handler APIs (ResourceEventHandler's OnAdd/OnUpdate/OnDelete). The ResourceEventHandler gives the application logic the change to execute customized logic for this resource change, an example is when there are cross-resources dependency like Deployment and DeploymentScale. On Deployment OnAdd event, Autoscaler needs to create a corresponding DeploymentScale object.

The ResourceChangeConsumer, ResourceReconciler, and ResourceEventHandler combination is the main path for keeping state in sync, between database and cache, and also between cross-resources. However, there are scenarios where this happy path is not sufficient to keep state in sync.

Example scenarios where resource state can get out of sync:
* MCS restart/failure. During the time it takes for MCS to startup, it is possible that some change occurred. By getting the latest
resource state from the database, MCS will rebuild the latest resource state, but it will not capture the change events that occured e.g. if Deployment was deleted, MCS will not have it in the cache (expected), and it will not know that something was deleted (change event) so it will not trigger a reconcile (ResourceReconciler). In the Autoscaler case, we will have an orphaned DeploymentScale.
* Database interruption. During reconcile (ResourceReconciler), it is possible that the database calls fail (after retries) due to outage (database/network). This means we are unable to apply the change to the cache or the ResourceEventHandler. In the case of a new Deployment created, the cache will not have this Deployment, and Autoscaler will not have the opportunity to create a DeploymentScale object.

To cover these scenarios, we introduce additional reconcile mechanisms:
1. Periodic resource resync
2. Application level customized periodic reconciler

Periodic resource resync (ResourceResync) is a generic mechanism. It periodically triggers a resync which will get the full resource
state from the database and force call reconcile (ResourceReconciler) for each of the resource. This will ensure that all resources have the chance to reconcile with the cache, and also give opportunity for ResourceEventHandler to handle missed resource changes. ResourceResync will also do a diff between the database state and the cache state to capture orphaned resources in the cache (deleted in databased but still in the cache). It will force call reconcile for each orphaned resource.

Unfortunately, ResourceResync is still not sufficient to cover all the cross-resources dependency scenarios. For example, on a Deployment delete change event, the Autoscaler's ResourceEventHandler processing could fail where it cannot delete the corresponding DeploymentScale object. We now have an orphaned DeploymentScale object. Deployment resync will not help because the
Deployment object has been deleted and so it will not trigger reconcile for that Deployment object again.

To cover this cross-resources scenarios, we need an application level periodic reconciler. This is application specific (cross-resources dependency are application logic). For Autoscaler, we have a reconcile (AutoscalerReconciler) that specific looks for orphaned DeploymentScale and cleans up.

Note: 
If we go with the approach where we delete the cross-resources dependency tree together from the database then we would be able to avoid the need for the application level customized periodic reconciler for most cases. For example, the service that is deleting a Deployment object from the database will also delete all other related (child) resources like DeploymentScale and DeploymentSchedule. Knative uses the k8s OwnerReference for cross-resources reference and for cascading delete when deleting a revision.

# Links
* [Scheduler](scheduler/README.md)
* [Autoscaler](autoscaler/README.md)