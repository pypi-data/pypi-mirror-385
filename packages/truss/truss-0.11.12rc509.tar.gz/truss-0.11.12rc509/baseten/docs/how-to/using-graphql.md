# Using GraphQL @ Baseten

While our Django backend features a number of [REST endpoints](https://en.wikipedia.org/wiki/Representational_state_transfer), nowadays it is strongly encouraged that the majority of _new_ network calls from the frontend leverage our [GraphQL](https://graphql.org/) endpoints, which are powered by the [Graphene](https://graphene-python.org/) Python library.

## Why GraphQL?

Your first question, apart from maybe _"what is GraphQL?"_, is probably _"why not just REST?"_. It's a fair question, so let's talk about it.

At a high level, GraphQL is a query language originally developed by Facebook (now Meta) that allows you to declaratively query the data you want from a server.

Where you might have previously made a POST request to a REST endpoint such as:

```
https://baseten.co/api/users/someUserID?fields=name,age
```

you would query it via GraphQL using something like:

```graphql
query UserQuery {
  user(id: "someUserID") {
    name
    email
  }
}
```

Much easier to read, isn't it? Outside of readability, GraphQL also gives us some other cool features:

🏗️ **Backs up data with a structured, queryable schema.** Did you accidentally query a field that doesn't exist? Maybe you passed in a number where it should have been a string? You're in luck... GraphQL will automatically error and let you know.

⚒️ **Automatic TypeScript types with the [GraphQL Codegen](https://graphql-code-generator.com/)** Seeing GraphQL features [built-in schema introspection](https://graphql.org/learn/introspection/), we can automatically generate TypeScript types to correspond with our backend types. Say hello to type safety across the stack! :wave:

🎨 **First-class IDE & syntax highlighting support.** It's more enjoyable to write code when it looks pretty. [VSCode](https://marketplace.visualstudio.com/items?itemName=GraphQL.vscode-graphql), along with several other editors, have extensions that provide syntax highlighting to `.graphql` and `.gql` files.

📖 **Auto-generating documentation.** Thanks again to GraphQL's schema introspection, many tools such as [Hoppscotch](https://hoppscotch.io) and [GraphiQL](https://github.com/graphql/graphiql) automatically generate browsable documentation for your GraphQL endpoints. There are also a handful of static site generators that can generate entire documentation sites based on your schema.

Pretty neat, huh?

## Writing GraphQL on the Frontend

There are a few rules of thumb when it comes to querying GraphQL from the frontend:

1. **Write GraphQL, not TypeScript.** The current codegen is configured to look specifically for `.gql` files (we chose `gql` over `graphql` because it's shorter). Don't write `.ts` files that use the `gql` tag or something else that generates a document node at runtime. The GraphQL codegen will automatically create document nodes for you in a `__generated__` directory next to your GraphQL code (more on this in the example below).
2. **Use a single file for each type of GraphQL document.** This refers to keeping a `mutations.gql`, `queries.gql`, `fragemnts.gql` and `subscriptions.gql` file next to your components (as needed) instead of creating a new file for each query/mutation/fragment/subscription.
3. **All queries/mutations/subscriptions should be as close to their point of usage as possible.** This means you _shouldn't_ place a GraphQL query in `baseten/pages/Application` if it is only being used in `baseten/pages/Models`. Not sure why you would, anyway – if a query is meant to be shared, put it in a logical shared location and use your best judgement.
4. **Don't put anything in `baseten/graphql`.** All GraphQL types are generated here (such as `User`, `Workflow`, etc.). This directory should not be used to hold shared queries or mutations, seeing sharing queries and mutations is not strongly encouraged. Only use it to import types as needed.

### Example

With all this said, let's run through a quick example. Let's use our query from above, which may not be an accurate query in the context of Baseten, but let's use it anyway as an example.

We first kickoff the GraphQL codegen by running

```
npm run start
```

_or_, if we _only_ want to run the codegen, we can run:

```
npm run codegen -- --watch
```

The codegen will now listen for any new changes in `.gql` files and automatically create TypeScript we can pass directly to our [Apollo GraphQL client](https://www.apollographql.com/docs/react/).

Next to our component, inside a file named `queries.gql`, we'll add our query:

```graphql
query UserQuery($id: ID!) {
  user(id: $id) {
    id # Adding the ID will help Apollo normalize this object in the cache
    name
    email
  }
}
```

Now, like magic, our codegen should automatically spit out the file `./__generated__/queries.generated.ts`.

From inside our component or Redux store, we can now pass our query as a [TypedDocumentNode](https://www.the-guild.dev/blog/typed-document-node) to the Apollo client:

```typescript
import { UserQueryDocument } from './__generated__/queries.generated.ts';

// Some time later...

const result = await client.query(UserQueryDocument, { id: "someUserID" })

console.log(`Hello ${result.data?.user?.name}!`);
```

Our `UserQueryDocument` will automatically tell Apollo the return type of our query, as well as the types of its variables, so the above call is entirely type safe!

> :bulb: Notice how our code doesn't specify where the `client` variable is coming from – this is because the answer to this can vary depending on where you're calling your query. Most of our GraphQL is currently being called from Redux async thunks, which store an instance of the Apollo client in its `extras` parameter ([see example](https://github.com/basetenlabs/baseten/blob/57d0621464d2f533055dffeca444722079cb263b/frontend/store/actions/Secrets/SecretsActions.ts#L40)).

As we attempt to move away from storing state in Redux, it may be beneficial to just use React hooks to query our data. Fortunately, our codegen already has us covered:

```tsx
import { useUserQuery } from './__generated__/queries.generated.ts';

const MyComponent() {
  const { data, loading } = useUserQuery();

  if (loading) {
    return <>Loading...</>
  }

  return <>Hello, {data?.user?.name}!</>;
}
```

## Writing GraphQL on the Backend

There isn't a ton to say here that can't be found in the Graphene documentation.

Most, if not all Graphene-related classes can be found inside [schema](/backend/workflows/schema) directories throughout the [backend](/backend) directory.

🚨 **However, a very important note:** once the GraphQL schema is modified, you _must run_ the following command to update the schema JSON before you can write any frontend queries that use your new fields or types:

```
poetry run manage.py export_schema
```

This dumps our schema to `frontend/schema.json`, which the codegen uses to validate frontend queries.

While we _could_ technically have the codegen introspect on-the-fly, it would become a royal pain when running the codegen on Github Actions, so we settled for this instead.

## FAQ

### My commit linting failed on the schema-codegen step. Why?

Occasionally your commit linting may fail and you'll see something like the following:

![GraphQL linting](images/graphql-lint.png)

This error may occur when your schema.json is updated during the lint stage, as it is configured to automatically export the GraphQL schema during the pre-commit hook.

**How to fix:** If this happens, first inspect the changes via:

```bash
$ git diff frontend/schema.json
```

and see if the changes are expected. If they are, then just commit the file to your branch. If they are not, there is a chance the JSON hasn't been exported since the backend was last modified. This can sometimes happen if you bypass the pre-commit hook via `git commit --no-verify`.

In this case, open a new PR with the updated schema file, which you can update via `poetry run manage.py export_schema`.

### Github Actions has failed with the error: "Unexpected local changes". Why?

Even though we have pre-commit hooks to prevent against this error, there is still the rare occasion in which the GraphQL schema or generated files may be different in the CI than they are locally. This might happen if you rebase or merge with master via the Github UI.

When Github Actions run, they run both the `export_schema` command _as well as_ the NPM `codegen` script to ensure that you've committed the latest version of the schema and your queries to the repo. If there is any discrepency, it will error.

**How to fix:** All you need to do is checkout your code, run `poetry run manage.py export_schema` or `npm run codegen` (depending on what the error says), and commit the changed files.

### I'm seeing changes in my commit that I don't expect. Why?

At one point there were some issues in which GraphQL files (`.gql`) or their generated counterparts would be picked up by linting.

**How to fix:** This should no longer be an issue, but if you see something unexpected, feel free to ping the [#js-react](https://basetenlabs.slack.com/archives/C03FX92R401) channel and ask about it.
