# Api Resources

Api resources are implementation agnostic schematic representations of Baseten
entities such as Applications and Worklets.

## How are api-resource schemas represented?

Using protobuf in [resources.proto](/proto/resources.proto)

## How/where are api-resources used?

Api resources are currently used for many cases of copy creation.

1. Application, Worklet, View, Query cloning
1. Starter apps
1. Model apps
1. Baseten internal apis for exporting resources as yaml and importing them.
    - For example to transfer applications from prod to staging and vice-versa

## How are api-resources exported to yaml?

Each api resource has a controller. Controller knows how to translate Django db
representation of the resource into the protobuf definition. The yaml is just
the protobuf in yaml form. Note that protobuf is a schema definition language,
that can represented in a variety of formats, including json and yaml. In fact,
our yaml export is done by first converting python protobuf representation to
json and then converting the json to yaml.

Api resources know about other resources. There is a notion of strong and weak
dependency. Strong dependency is like a contains relationship, e.g. an
Application contains Worklets. A weak dependency is like a reference, e.g. a
Node can refer to UDM table, it does not contain it. A UDM table may be
referenced by many applications. Export mechanism allows exporting just the
resource, or the strong dependency graph or the strong and weak dependency
graph.

When cloning an application, only the strong dependency graph is exported.
There is no need to export the weak deps as they would already exist. When
exporting starter apps, both strong and weak deps are exported, because a user
account likely wouldn't have any of them.

## How are api-resources imported

Api resource controllers help with import as well. The process of converting the
canonical representation of a resources (protobuf) to Django entities is called
materialization. Resource dependencies are even more important during
materialization; many resources simply cannot be created correctly without other
resources. During materialization a resource can ask for its dependencies to be
provided. The materialization engine can control how to fulfill these
dependencies to control behavior. e.g., in certain scenarios the engine may only
provide dependencies by looking them up in Django db models. In others,
it may look into a provided set of definitions and materialize resources
as needed. It may even be a combination. At the outermost level, this can be
controlled via a materialization policy.

When it comes to the materialization logic for an individual resource it's quite
simple. The controller looks at the provided resource definition, identifies the
dependencies it needs and asks for them. Using the dependencies and the schema
defintion it then constructs the Django entities for the resource.

For example, a Worket needs an Application(Workflow) to exist in and thus
depends on it. The Worklet controller asks for the Application entities to be
provided. The controller creates Worklet and WorkletVersion entities based on
schema details and attaches the created Worklet to the WorkflowVersion.

### What is `finalize` in resource import?

There are sometimes circular dependencies among resources. e.g. View A may have
an action to jump to View B, and View B may have an action to jump to View B.
This is infact quite a common occurance, because it makes sense to make it easy
to jump back and forth between views. Similarly, a Worklet Node (a special node
that points to a worklet), can point to the worklet it's contained in. The
simplest example is that of Worklet and Node. The Node Django model can simply
not be constructed without referring to a Worklet, and Worklet refers to the
node ids in its node-graph.

Let's say we want to import an application with the first scenario above. We
reach View A which needs View B, so we try to construct View B first. But View B
needs View A and we hit a wall. A common solution to breaking circular
dependencies is bootstrapping, instead of constructing a full entity create a
partially constructed one and pass that around. This is what we do. We let the
resource partially construct itself and delay binding some or all of the
dependencies. Resource controller can provide finalize function/callback to the
import engine, which will be called with fully constructed entities for late
binding.

### Application cloning example

Application cloning is a special, somewhat simple, case in which the export and
import happen immediately. This all happens in-memory and we don't need to
construct yamls. We export the application along with its strong (contains)
dependencies, i.e. Worklets and Views and CodeFiles. Worklets in turn contain
Nodes which are exported too. Nodes may refer to models but those are not
contained and thus not exported. Ultimately, we end up with a list of (python)
protobufs.

We then import this list of resources one by one. We don't require resources to
be listed in dependency order. We simply go one by one but also materialize
resources as needed. Say a Node is the first listed resource. When we try to
materialize it, it would ask to be provided the Worklet resource, so we try to
materialize that first. But the Worklet needs the Application, so we go
materialize the Application.

One problem here is that a Node can't be constructed without a Worklet; it
absolutely needs the Worklet, but a Worklet also needs the node id. This is
because the node graph in Worklet resource refers to node ids in the exported
application. This graph needs to be updated with node ids of newly imported
application. We can't know these ids until the new Nodes are created. But Nodes
need the Worlet to be created first. This is a place where the finalize
mechanism comes in handy. Worklet constructs itself initially but doesn't ask for
nodes and doesn't update the node graph. Instead, it provides a finalize
function, asks for and updates node ids in the node graph there. So, in the
first pass everything gets constructed, albeit some resources such as Worklets
are not finished. In the second pass, Worklets get finalized, updating node
ids, which are now available, in the node graph.

#### Side Note

One may topologically sort resources to make sure dependencies are always
available but this would be too fragile and creates the burden of performing
topological sort on the export side and preservation of it until import. e.g. if
resoure yamls exist as text files in a git repo, someone may move around
resources and change the order. So, we don't require resources to be listed in
dependency order. Instead we go one by one but materialize resources as needed.
