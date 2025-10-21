# Truss Base

Truss base is a library that duplicates basic functionality of truss. This enables backend services 
to reference common definitions, such as TrussConfig. This is useful for deploying from the UI.

Truss Base exists as it's own package (as opposed to living in baseten_shared) to avoid dependency issues for services it doesn't need to be apart of (e.g. Operator)

We weighed the following approaches for enabling this functionality
* truss in django: Import truss in its entirety and run truss push or some equivalent via some subprocess or containerized environment
* truss base: Section off a portion of truss, e.g. truss_base and refactor truss to import/reexport this package as necessary. Django can then import truss_base .
* duplicate definitions: Manually copy over the pieces of truss we exclusively need for constructing and pushing the truss config.

Our reasoning for selecting duplicate definitions is as follows: 
* We all strongly felt that truss in django was an antipattern and fairly risky, as we don't have a good way of preventing circular dependencies (e.g. django invokes truss push which then calls django service)
* Sectioning out truss base was appealing because we avoid repeating ourselves, but we then couple development in truss to dependency compatibility in django. We felt like this risk to development velocity wasn't worth the benefits of a shared package - specifically at this early stage. "How do people know what can/can't be in truss base" is hard to know, especially since (1) Core Product isn't the only team that works on truss and (2) truss and truss_base are in a separate repo entirely, making dependency sync hard.
* In going foward with duplicate definitions, we are accepting the risk that over time we introduce some drift in the config via params that are only used in API-driven deploys vs. CLI-driven deploys. We'll keep a pulse on the maintenance burden, and if it becomes a big enough thorn, it might motivate a move for Truss to join the monorepo or adoption of the truss base strategy
