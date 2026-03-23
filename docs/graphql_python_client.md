# Dagster GraphQL Python Client

Dagster provides an official Python client for interfacing with Dagster's GraphQL API. The client is available in the `dagster-graphql` package.

## Installation

```bash
pip install dagster-graphql
```

## DagsterGraphQLClient

```python
from dagster_graphql import DagsterGraphQLClient

client = DagsterGraphQLClient("localhost", port_number=3000)
status = client.get_run_status(SOME_RUN_ID)
```

The `DagsterGraphQLClient` utilizes the `gql` library to dispatch queries over HTTP to a remote Dagster GraphQL Server. All operations on this client are synchronous.

### Constructor Parameters

- `hostname` (str): Hostname for the Dagster GraphQL API, like `localhost` or `YOUR_ORG_HERE.dagster.cloud`.
- `port_number` (Optional[int]): Port number to connect to on the host. Defaults to None.
- `transport` (Optional[Transport]): A custom transport to use to connect to the GraphQL API with (e.g. for custom auth). Defaults to None.
- `use_https` (bool): Whether to use https in the URL connection string for the GraphQL API. Defaults to False.
- `timeout` (int): Number of seconds before requests should time out. Defaults to 60.
- `headers` (Optional[Dict[str, str]]): Additional headers to include in the request. To use this client in Dagster Cloud, set the `Dagster-Cloud-Api-Token` header to a user token generated in the Dagster Cloud UI.

Raises `ConnectionError` if the client cannot connect to the host.

## Methods

### get_run_status(run_id)

Get the status of a given Pipeline Run.

**Parameters:**
- `run_id` (str): run id of the requested pipeline run.

**Raises:**
- `DagsterGraphQLClientError("PipelineNotFoundError", message)` – if the requested run id is not found
- `DagsterGraphQLClientError("PythonError", message)` – on internal framework errors

**Returns:** a status Enum describing the state of the requested pipeline run (type: `DagsterRunStatus`).

### submit_job_execution(...)

Submits a job with attached configuration for execution.

**Parameters:**
- `job_name` (str): The job's name
- `repository_location_name` (Optional[str]): The name of the repository location where the job is located. If omitted, the client will try to infer the repository location from the available options on the Dagster deployment. Defaults to None.
- `repository_name` (Optional[str]): The name of the repository where the job is located. If omitted, the client will try to infer the repository from the available options on the Dagster deployment. Defaults to None.
- `run_config` (Optional[Union[RunConfig, Mapping[str, Any]]]): The run config to execute the job with. Must conform to the constraints of the config schema for the job. If it does not, the client will throw a `DagsterGraphQLClientError` with a message of `JobConfigValidationInvalid`. Defaults to None.
- `tags` (Optional[Dict[str, Any]]): A set of tags to add to the job execution.
- `op_selection` (Optional[Sequence[str]]): A list of ops to execute.
- `asset_selection` (Optional[Sequence[CoercibleToAssetKey]]): A list of asset keys to execute.

**Raises:**
- `DagsterGraphQLClientError("InvalidStepError", invalid_step_key)` – the job has an invalid step
- `DagsterGraphQLClientError("InvalidOutputError", body=error_object)` – some solid has an invalid output within the job. The error_object is of type `dagster_graphql.InvalidOutputErrorInfo`.
- `DagsterGraphQLClientError("RunConflict", message)` – a conflicting job run already exists in run storage.
- `DagsterGraphQLClientError("PipelineConfigurationInvalid", invalid_step_key)` – the run_config is not in the expected format for the job
- `DagsterGraphQLClientError("JobNotFoundError", message)` – the requested job does not exist
- `DagsterGraphQLClientError("PythonError", message)` – an internal framework error occurred

**Returns:** run id of the submitted pipeline run (type: `str`).

### reload_repository_location(repository_location_name)

Reloads a Dagster Repository Location, which reloads all repositories in that repository location. This is useful for refreshing the Dagster UI without restarting the server.

**Parameters:**
- `repository_location_name` (str): The name of the repository location

**Returns:** Object with information about the result of the reload request (type: `ReloadRepositoryLocationInfo`).

### shutdown_repository_location(repository_location_name)

> **Deprecated**: This API will be removed in version 2.0.

Shuts down the server that is serving metadata for the provided repository location. This is primarily useful when you want the server to be restarted by the compute environment in which it is running (for example, in Kubernetes, the pod in which the server is running will automatically restart when the server is shut down, and the repository metadata will be reloaded).

**Parameters:**
- `repository_location_name` (str): The name of the repository location

**Returns:** Object with information about the result of the reload request (type: `ShutdownRepositoryLocationInfo`).

## Error Types

### DagsterGraphQLClientError

Exception raised when a GraphQL client operation fails.

### InvalidOutputErrorInfo

Gives information about an InvalidOutputError from submitting a pipeline for execution from GraphQL.

**Parameters:**
- `step_key` (str): key of the step that failed
- `invalid_output_name` (str): the name of the invalid output from the given step

### ReloadRepositoryLocationInfo

Gives information about the result of reloading a Dagster repository location with a GraphQL mutation.

**Parameters:**
- `status` (ReloadRepositoryLocationStatus): The status of the reload repository location mutation
- `failure_type` (Optional[str]): the failure type if status == FAILURE. Can be one of `ReloadNotSupported`, `RepositoryLocationNotFound`, or `RepositoryLocationLoadFailure`. Defaults to None.
- `message` (Optional[str]): the failure message/reason if status == FAILURE. Defaults to None.

### ReloadRepositoryLocationStatus

Enum describing the status of a GraphQL mutation to reload a Dagster repository location. Can be either `ReloadRepositoryLocationStatus.SUCCESS` or `ReloadRepositoryLocationStatus.FAILURE`.
