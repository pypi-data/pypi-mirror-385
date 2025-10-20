# Version

Types:

```python
from ractorlabs.types import VersionRetrieveResponse
```

Methods:

- <code title="get /version">client.version.<a href="./src/ractorlabs/resources/version.py">retrieve</a>() -> <a href="./src/ractorlabs/types/version_retrieve_response.py">VersionRetrieveResponse</a></code>

# Operators

Types:

```python
from ractorlabs.types import LoginResponse, Operator, OperatorListResponse
```

Methods:

- <code title="post /operators">client.operators.<a href="./src/ractorlabs/resources/operators.py">create</a>(\*\*<a href="src/ractorlabs/types/operator_create_params.py">params</a>) -> <a href="./src/ractorlabs/types/operator.py">Operator</a></code>
- <code title="get /operators/{name}">client.operators.<a href="./src/ractorlabs/resources/operators.py">retrieve</a>(name) -> <a href="./src/ractorlabs/types/operator.py">Operator</a></code>
- <code title="put /operators/{name}">client.operators.<a href="./src/ractorlabs/resources/operators.py">update</a>(name, \*\*<a href="src/ractorlabs/types/operator_update_params.py">params</a>) -> <a href="./src/ractorlabs/types/operator.py">Operator</a></code>
- <code title="get /operators">client.operators.<a href="./src/ractorlabs/resources/operators.py">list</a>() -> <a href="./src/ractorlabs/types/operator_list_response.py">OperatorListResponse</a></code>
- <code title="delete /operators/{name}">client.operators.<a href="./src/ractorlabs/resources/operators.py">delete</a>(name) -> None</code>
- <code title="post /operators/{name}/login">client.operators.<a href="./src/ractorlabs/resources/operators.py">login</a>(name, \*\*<a href="src/ractorlabs/types/operator_login_params.py">params</a>) -> <a href="./src/ractorlabs/types/login_response.py">LoginResponse</a></code>
- <code title="put /operators/{name}/password">client.operators.<a href="./src/ractorlabs/resources/operators.py">update_password</a>(name, \*\*<a href="src/ractorlabs/types/operator_update_password_params.py">params</a>) -> None</code>

# Published

## Sessions

Types:

```python
from ractorlabs.types.published import Session, SessionListResponse
```

Methods:

- <code title="get /published/sessions/{name}">client.published.sessions.<a href="./src/ractorlabs/resources/published/sessions.py">retrieve</a>(name) -> <a href="./src/ractorlabs/types/published/session.py">Session</a></code>
- <code title="get /published/sessions">client.published.sessions.<a href="./src/ractorlabs/resources/published/sessions.py">list</a>() -> <a href="./src/ractorlabs/types/published/session_list_response.py">SessionListResponse</a></code>

# Auth

Types:

```python
from ractorlabs.types import AuthRetrieveCurrentPrincipalResponse
```

Methods:

- <code title="post /auth/token">client.auth.<a href="./src/ractorlabs/resources/auth.py">create_token</a>(\*\*<a href="src/ractorlabs/types/auth_create_token_params.py">params</a>) -> <a href="./src/ractorlabs/types/login_response.py">LoginResponse</a></code>
- <code title="get /auth">client.auth.<a href="./src/ractorlabs/resources/auth.py">retrieve_current_principal</a>() -> <a href="./src/ractorlabs/types/auth_retrieve_current_principal_response.py">AuthRetrieveCurrentPrincipalResponse</a></code>

# Blocklist

Types:

```python
from ractorlabs.types import (
    BlockRequest,
    BlocklistListResponse,
    BlocklistBlockResponse,
    BlocklistUnblockResponse,
)
```

Methods:

- <code title="get /blocklist">client.blocklist.<a href="./src/ractorlabs/resources/blocklist.py">list</a>() -> <a href="./src/ractorlabs/types/blocklist_list_response.py">BlocklistListResponse</a></code>
- <code title="post /blocklist/block">client.blocklist.<a href="./src/ractorlabs/resources/blocklist.py">block</a>(\*\*<a href="src/ractorlabs/types/blocklist_block_params.py">params</a>) -> <a href="./src/ractorlabs/types/blocklist_block_response.py">BlocklistBlockResponse</a></code>
- <code title="post /blocklist/unblock">client.blocklist.<a href="./src/ractorlabs/resources/blocklist.py">unblock</a>(\*\*<a href="src/ractorlabs/types/blocklist_unblock_params.py">params</a>) -> <a href="./src/ractorlabs/types/blocklist_unblock_response.py">BlocklistUnblockResponse</a></code>

# Sessions

Types:

```python
from ractorlabs.types import (
    SessionListResponse,
    SessionCancelResponse,
    SessionGetRuntimeResponse,
    SessionMarkBusyResponse,
    SessionMarkIdleResponse,
    SessionUpdateStateResponse,
)
```

Methods:

- <code title="post /sessions">client.sessions.<a href="./src/ractorlabs/resources/sessions/sessions.py">create</a>(\*\*<a href="src/ractorlabs/types/session_create_params.py">params</a>) -> <a href="./src/ractorlabs/types/published/session.py">Session</a></code>
- <code title="get /sessions/{name}">client.sessions.<a href="./src/ractorlabs/resources/sessions/sessions.py">retrieve</a>(name) -> <a href="./src/ractorlabs/types/published/session.py">Session</a></code>
- <code title="put /sessions/{name}">client.sessions.<a href="./src/ractorlabs/resources/sessions/sessions.py">update</a>(name, \*\*<a href="src/ractorlabs/types/session_update_params.py">params</a>) -> <a href="./src/ractorlabs/types/published/session.py">Session</a></code>
- <code title="get /sessions">client.sessions.<a href="./src/ractorlabs/resources/sessions/sessions.py">list</a>(\*\*<a href="src/ractorlabs/types/session_list_params.py">params</a>) -> <a href="./src/ractorlabs/types/session_list_response.py">SessionListResponse</a></code>
- <code title="delete /sessions/{name}">client.sessions.<a href="./src/ractorlabs/resources/sessions/sessions.py">delete</a>(name) -> None</code>
- <code title="post /sessions/{name}/branch">client.sessions.<a href="./src/ractorlabs/resources/sessions/sessions.py">branch</a>(path_name, \*\*<a href="src/ractorlabs/types/session_branch_params.py">params</a>) -> <a href="./src/ractorlabs/types/published/session.py">Session</a></code>
- <code title="post /sessions/{name}/cancel">client.sessions.<a href="./src/ractorlabs/resources/sessions/sessions.py">cancel</a>(name) -> <a href="./src/ractorlabs/types/session_cancel_response.py">SessionCancelResponse</a></code>
- <code title="get /sessions/{name}/runtime">client.sessions.<a href="./src/ractorlabs/resources/sessions/sessions.py">get_runtime</a>(name) -> <a href="./src/ractorlabs/types/session_get_runtime_response.py">SessionGetRuntimeResponse</a></code>
- <code title="post /sessions/{name}/busy">client.sessions.<a href="./src/ractorlabs/resources/sessions/sessions.py">mark_busy</a>(name) -> <a href="./src/ractorlabs/types/session_mark_busy_response.py">SessionMarkBusyResponse</a></code>
- <code title="post /sessions/{name}/idle">client.sessions.<a href="./src/ractorlabs/resources/sessions/sessions.py">mark_idle</a>(name) -> <a href="./src/ractorlabs/types/session_mark_idle_response.py">SessionMarkIdleResponse</a></code>
- <code title="post /sessions/{name}/publish">client.sessions.<a href="./src/ractorlabs/resources/sessions/sessions.py">publish</a>(name, \*\*<a href="src/ractorlabs/types/session_publish_params.py">params</a>) -> None</code>
- <code title="post /sessions/{name}/sleep">client.sessions.<a href="./src/ractorlabs/resources/sessions/sessions.py">sleep</a>(name, \*\*<a href="src/ractorlabs/types/session_sleep_params.py">params</a>) -> <a href="./src/ractorlabs/types/published/session.py">Session</a></code>
- <code title="post /sessions/{name}/unpublish">client.sessions.<a href="./src/ractorlabs/resources/sessions/sessions.py">unpublish</a>(name) -> None</code>
- <code title="put /sessions/{name}/state">client.sessions.<a href="./src/ractorlabs/resources/sessions/sessions.py">update_state</a>(name, \*\*<a href="src/ractorlabs/types/session_update_state_params.py">params</a>) -> <a href="./src/ractorlabs/types/session_update_state_response.py">SessionUpdateStateResponse</a></code>
- <code title="post /sessions/{name}/wake">client.sessions.<a href="./src/ractorlabs/resources/sessions/sessions.py">wake</a>(name, \*\*<a href="src/ractorlabs/types/session_wake_params.py">params</a>) -> <a href="./src/ractorlabs/types/published/session.py">Session</a></code>

## Context

Types:

```python
from ractorlabs.types.sessions import SessionContextUsage, ContextReportUsageResponse
```

Methods:

- <code title="post /sessions/{name}/context/clear">client.sessions.context.<a href="./src/ractorlabs/resources/sessions/context.py">clear</a>(name) -> <a href="./src/ractorlabs/types/sessions/session_context_usage.py">SessionContextUsage</a></code>
- <code title="post /sessions/{name}/context/compact">client.sessions.context.<a href="./src/ractorlabs/resources/sessions/context.py">compact</a>(name) -> <a href="./src/ractorlabs/types/sessions/session_context_usage.py">SessionContextUsage</a></code>
- <code title="get /sessions/{name}/context">client.sessions.context.<a href="./src/ractorlabs/resources/sessions/context.py">get_usage</a>(name) -> <a href="./src/ractorlabs/types/sessions/session_context_usage.py">SessionContextUsage</a></code>
- <code title="post /sessions/{name}/context/usage">client.sessions.context.<a href="./src/ractorlabs/resources/sessions/context.py">report_usage</a>(name, \*\*<a href="src/ractorlabs/types/sessions/context_report_usage_params.py">params</a>) -> <a href="./src/ractorlabs/types/sessions/context_report_usage_response.py">ContextReportUsageResponse</a></code>

## Responses

Types:

```python
from ractorlabs.types.sessions import ResponseView, ResponseListResponse, ResponseCountResponse
```

Methods:

- <code title="post /sessions/{name}/responses">client.sessions.responses.<a href="./src/ractorlabs/resources/sessions/responses.py">create</a>(name, \*\*<a href="src/ractorlabs/types/sessions/response_create_params.py">params</a>) -> <a href="./src/ractorlabs/types/sessions/response_view.py">ResponseView</a></code>
- <code title="get /sessions/{name}/responses/{id}">client.sessions.responses.<a href="./src/ractorlabs/resources/sessions/responses.py">retrieve</a>(id, \*, name) -> <a href="./src/ractorlabs/types/sessions/response_view.py">ResponseView</a></code>
- <code title="put /sessions/{name}/responses/{id}">client.sessions.responses.<a href="./src/ractorlabs/resources/sessions/responses.py">update</a>(id, \*, name, \*\*<a href="src/ractorlabs/types/sessions/response_update_params.py">params</a>) -> <a href="./src/ractorlabs/types/sessions/response_view.py">ResponseView</a></code>
- <code title="get /sessions/{name}/responses">client.sessions.responses.<a href="./src/ractorlabs/resources/sessions/responses.py">list</a>(name, \*\*<a href="src/ractorlabs/types/sessions/response_list_params.py">params</a>) -> <a href="./src/ractorlabs/types/sessions/response_list_response.py">ResponseListResponse</a></code>
- <code title="get /sessions/{name}/responses/count">client.sessions.responses.<a href="./src/ractorlabs/resources/sessions/responses.py">count</a>(name) -> <a href="./src/ractorlabs/types/sessions/response_count_response.py">ResponseCountResponse</a></code>

## Files

Types:

```python
from ractorlabs.types.sessions import FileDeleteResponse, FileGetMetadataResponse
```

Methods:

- <code title="delete /sessions/{name}/files/delete/{path}">client.sessions.files.<a href="./src/ractorlabs/resources/sessions/files/files.py">delete</a>(path, \*, name) -> <a href="./src/ractorlabs/types/sessions/file_delete_response.py">FileDeleteResponse</a></code>
- <code title="get /sessions/{name}/files/metadata/{path}">client.sessions.files.<a href="./src/ractorlabs/resources/sessions/files/files.py">get_metadata</a>(path, \*, name) -> <a href="./src/ractorlabs/types/sessions/file_get_metadata_response.py">FileGetMetadataResponse</a></code>
- <code title="get /sessions/{name}/files/read/{path}">client.sessions.files.<a href="./src/ractorlabs/resources/sessions/files/files.py">read</a>(path, \*, name) -> BinaryAPIResponse</code>

### List

Types:

```python
from ractorlabs.types.sessions.files import FileList
```

# Responses

Methods:

- <code title="get /responses/{id}">client.responses.<a href="./src/ractorlabs/resources/responses.py">retrieve</a>(id) -> <a href="./src/ractorlabs/types/sessions/response_view.py">ResponseView</a></code>
