# Typed fixtures

## Overview

Backend responses are mocked for core Model/Chain flows due to the test environment (on CircleCI) not having a k8s cluster (like Minikube).

Note that the fixtures are typed. For instance:

```ts
import { ChainQuery } from '../../../src/sections/Workspace/__generated__/queries.generated';

type MockChain = {
  data: ChainQuery;
};

const MOCK_CHAIN: MockChain = {
  // Fixture content.
};
```

This allows us to statically determine when the GQL schema has drifted from the fixture definitions. A drift will cause a GitHub Actions CI check to fail on an open PR. This means we can catch and fix discrepancies at compile time instead of wondering why Cypress tests suddenly stopped working.

## Updating fixtures

If we're trying to accommodate a relatively minor GQL schema change, it's likely we can simply update the existing fixtures. If it's a significant change, it might be easier to create new fixtures for the affected queries and mutations.

## Creating fixtures

To define these fixtures, we grab real data from https://app.staging.baseten.co. Take the following steps to get started:

1. Create a new staging account or delete all Models/Chains on an existing staging account.
1. Create one Model and one Chain. Good examples are [Bert](https://github.com/basetenlabs/truss-examples/tree/4436830e5154ec4de7bb9c4641f8038b68d1cbcb/01-getting-started-bert) (for Models) and [Hello World](https://docs.baseten.co/chains/getting-started#example-hello-world) (for Chains).
1. Load the Workspace, Model, and Chain pages with the network tab open in the browser dev tools. Copy over the responses for the various GQL queries/mutations into test fixtures.

If you're trying to create a fixture for a particular GQL query or mutation, there's a pattern we can follow that makes this step easier. For instance, if you're trying to create a fixture for `/graphql/?opName=Chain`, you can do a global search for where the `ChainQuery` generated type is defined and import it (refer to code snippet above). The pattern for finding the corresponding type for an operation is basically `<operation-name>Query` or `<operation-name>Mutation`.

When updating one fixture (e.g. Chain), you'll probably have to update related fixtures such as Chain Stable Environments, Chainlets, etc. We have many different GQL queries with significant overlap in the selected fields, which means there will be a lot of duplicated information across fixtures. This is a little unfortunate but mocking at the `frontend <> Django` level is still significantly easier than mocking at the `Django <> Operator` or `Operator <> k8s` levels.

When updating mutation response fixtures, make sure to think through the steps because some mutations can only be performed once per Model or Chain, such as promoting to production (once a production environment is created, it can't be deleted). If you forget to copy some of the responses before a point of no return, you'll have to recreate the Model or Chain, which can be a cumbersome process.

## Mocking interactions

To mock the interactions between the frontend and the backend, we have something of a "mock backend" in the form of a [mock store](../common/mock-store.ts). Most of the fixtures are stored here and intercepted GQL queries fetch data from this store instead of the actual Django backend. As such, mutations should update the fixtures that are stored here to capture real interactions between the frontend and Django.

To ensure that the fixtures are reset to their initial state after each test, we use the `immer` library's `produce` function to create updated fixtures without affecting the original fixtures in-place. You can find examples of this in [`helpers.ts`](../common/helpers.ts).
