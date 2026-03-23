# Dagster GraphQL API

The GraphQL API is still evolving and is subject to breaking changes. A large portion of the API is primarily for internal use by the Dagster webserver.

Dagster exposes a GraphQL API that allows clients to interact with Dagster programmatically. The API allows users to:
- Query information about Dagster runs, both historical and currently executing
- Retrieve metadata about repositories, jobs, and ops, such as dependency structure and config schemas
- Launch job executions and re-executions, allowing users to trigger executions on custom events

## Using the GraphQL API

The GraphQL API is served from the Dagster webserver. To start the server, run:

```bash
dg dev
```

The webserver serves the GraphQL endpoint at the `/graphql` endpoint. If you are running the webserver locally on port 3000, you can access the API at `http://localhost:3000/graphql`.

## Using the GraphQL Playground

You can access the GraphQL Playground by navigating to the `/graphql` route in your browser. The GraphQL playground contains the full GraphQL schema and an interactive playground to write and test queries and mutations.

## Exploring the GraphQL Schema and Documentation

Clicking on the Docs tab on the right edge of the playground opens up interactive documentation for the GraphQL API. The interactive documentation is the best way to explore the API and get information about which fields are available on the queries and mutations.

## Example Queries

### Get a List of Dagster Runs

You may eventually accumulate too many runs to return in one query. The `runsOrError` query takes in optional `cursor` and `limit` arguments for pagination:

```graphql
query PaginatedRunsQuery($cursor: String) {
  runsOrError(
    cursor: $cursor
    limit: 10
  ) {
    __typename
    ... on Runs {
      results {
        runId
        jobName
        status
        runConfigYaml
        startTime
        endTime
      }
    }
  }
}
```

### Filtering Runs

The `runsOrError` query also takes in an optional `filter` argument, of type `RunsFilter`. This query allows you to filter runs by:
- run ID
- job name
- tags
- statuses

For example, the following query will return all failed runs:

```graphql
query FilteredRunsQuery($cursor: String) {
  runsOrError(
    filter: { statuses: [FAILURE] }
    cursor: $cursor
    limit: 10
  ) {
    __typename
    ... on Runs {
      results {
        runId
        jobName
        status
        runConfigYaml
        startTime
        endTime
      }
    }
  }
}
```

### Get a List of Repositories

This query returns the names and location names of all the repositories currently loaded:

```graphql
query RepositoriesQuery {
  repositoriesOrError {
    ... on RepositoryConnection {
      nodes {
        name
        location {
          name
        }
      }
    }
  }
}
```

### Get a List of Jobs Within a Repository

Given a repository, this query returns the names of all the jobs in the repository. This query takes a `selector`, which is of type `RepositorySelector`. A repository selector consists of both the repository location name and repository name.

```graphql
query JobsQuery(
  $repositoryLocationName: String!
  $repositoryName: String!
) {
  repositoryOrError(
    repositorySelector: {
      repositoryLocationName: $repositoryLocationName
      repositoryName: $repositoryName
    }
  ) {
    ... on Repository {
      jobs {
        name
      }
    }
  }
}
```

### Launch a Run

To launch a run, use the `launchRun` mutation. The required arguments are:
- `selector` - A dictionary that contains the repository location name, repository name, and job name.
- `runConfigData` - The run config for the job execution. Note that `runConfigData` is of type `RunConfigData`. This type is used when passing in an arbitrary object for run config. It is any-typed in the GraphQL type system but must conform to the constraints of the config schema for the job. If it doesn't, the mutation returns a `RunConfigValidationInvalid` response.

```graphql
mutation LaunchRunMutation(
  $repositoryLocationName: String!
  $repositoryName: String!
  $jobName: String!
  $runConfigData: RunConfigData!
) {
  launchRun(
    executionParams: {
      selector: {
        repositoryLocationName: $repositoryLocationName
        repositoryName: $repositoryName
        jobName: $jobName
      }
      runConfigData: $runConfigData
    }
  ) {
    __typename
    ... on LaunchRunSuccess {
      run {
        runId
      }
    }
    ... on RunConfigValidationInvalid {
      errors {
        message
        reason
      }
    }
    ... on PythonError {
      message
    }
  }
}
```

### Terminate an In-Progress Run

If you want to stop execution of an in-progress run, use the `terminateRun` mutation. The only required argument is the ID of the run.

```graphql
mutation TerminateRun($runId: String!) {
  terminateRun(runId: $runId) {
    __typename
    ... on TerminateRunSuccess {
      run {
        runId
      }
    }
    ... on TerminateRunFailure {
      message
    }
    ... on RunNotFoundError {
      runId
    }
    ... on PythonError {
      message
      stack
    }
  }
}
```
