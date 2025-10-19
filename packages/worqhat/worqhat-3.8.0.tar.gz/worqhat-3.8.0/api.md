# Worqhat

Types:

```python
from worqhat.types import GetServerInfoResponse
```

Methods:

- <code title="get /">client.<a href="./src/worqhat/_client.py">get_server_info</a>() -> <a href="./src/worqhat/types/get_server_info_response.py">GetServerInfoResponse</a></code>

# DB

Types:

```python
from worqhat.types import (
    DBDeleteRecordsResponse,
    DBExecuteBatchResponse,
    DBExecuteQueryResponse,
    DBInsertRecordResponse,
    DBProcessNlQueryResponse,
    DBUpdateRecordsResponse,
)
```

Methods:

- <code title="delete /db/delete">client.db.<a href="./src/worqhat/resources/db/db.py">delete_records</a>(\*\*<a href="src/worqhat/types/db_delete_records_params.py">params</a>) -> <a href="./src/worqhat/types/db_delete_records_response.py">DBDeleteRecordsResponse</a></code>
- <code title="post /db/batch">client.db.<a href="./src/worqhat/resources/db/db.py">execute_batch</a>(\*\*<a href="src/worqhat/types/db_execute_batch_params.py">params</a>) -> <a href="./src/worqhat/types/db_execute_batch_response.py">DBExecuteBatchResponse</a></code>
- <code title="post /db/query">client.db.<a href="./src/worqhat/resources/db/db.py">execute_query</a>(\*\*<a href="src/worqhat/types/db_execute_query_params.py">params</a>) -> <a href="./src/worqhat/types/db_execute_query_response.py">DBExecuteQueryResponse</a></code>
- <code title="post /db/insert">client.db.<a href="./src/worqhat/resources/db/db.py">insert_record</a>(\*\*<a href="src/worqhat/types/db_insert_record_params.py">params</a>) -> <a href="./src/worqhat/types/db_insert_record_response.py">DBInsertRecordResponse</a></code>
- <code title="post /db/nl-query">client.db.<a href="./src/worqhat/resources/db/db.py">process_nl_query</a>(\*\*<a href="src/worqhat/types/db_process_nl_query_params.py">params</a>) -> <a href="./src/worqhat/types/db_process_nl_query_response.py">DBProcessNlQueryResponse</a></code>
- <code title="put /db/update">client.db.<a href="./src/worqhat/resources/db/db.py">update_records</a>(\*\*<a href="src/worqhat/types/db_update_records_params.py">params</a>) -> <a href="./src/worqhat/types/db_update_records_response.py">DBUpdateRecordsResponse</a></code>

## Tables

Types:

```python
from worqhat.types.db import (
    TableListResponse,
    TableGetRowCountResponse,
    TableRetrieveSchemaResponse,
)
```

Methods:

- <code title="get /db/tables">client.db.tables.<a href="./src/worqhat/resources/db/tables.py">list</a>(\*\*<a href="src/worqhat/types/db/table_list_params.py">params</a>) -> <a href="./src/worqhat/types/db/table_list_response.py">TableListResponse</a></code>
- <code title="get /db/tables/{tableName}/count">client.db.tables.<a href="./src/worqhat/resources/db/tables.py">get_row_count</a>(table_name, \*\*<a href="src/worqhat/types/db/table_get_row_count_params.py">params</a>) -> <a href="./src/worqhat/types/db/table_get_row_count_response.py">TableGetRowCountResponse</a></code>
- <code title="get /db/tables/{tableName}/schema">client.db.tables.<a href="./src/worqhat/resources/db/tables.py">retrieve_schema</a>(table_name, \*\*<a href="src/worqhat/types/db/table_retrieve_schema_params.py">params</a>) -> <a href="./src/worqhat/types/db/table_retrieve_schema_response.py">TableRetrieveSchemaResponse</a></code>

# Health

Types:

```python
from worqhat.types import HealthCheckResponse
```

Methods:

- <code title="get /health">client.health.<a href="./src/worqhat/resources/health.py">check</a>() -> <a href="./src/worqhat/types/health_check_response.py">HealthCheckResponse</a></code>

# Flows

Types:

```python
from worqhat.types import (
    FlowGetMetricsResponse,
    FlowTriggerWithFileResponse,
    FlowTriggerWithPayloadResponse,
)
```

Methods:

- <code title="get /flows/metrics">client.flows.<a href="./src/worqhat/resources/flows.py">get_metrics</a>(\*\*<a href="src/worqhat/types/flow_get_metrics_params.py">params</a>) -> <a href="./src/worqhat/types/flow_get_metrics_response.py">FlowGetMetricsResponse</a></code>
- <code title="post /flows/file/{flowId}">client.flows.<a href="./src/worqhat/resources/flows.py">trigger_with_file</a>(flow_id, \*\*<a href="src/worqhat/types/flow_trigger_with_file_params.py">params</a>) -> <a href="./src/worqhat/types/flow_trigger_with_file_response.py">FlowTriggerWithFileResponse</a></code>
- <code title="post /flows/trigger/{flowId}">client.flows.<a href="./src/worqhat/resources/flows.py">trigger_with_payload</a>(flow_id, \*\*<a href="src/worqhat/types/flow_trigger_with_payload_params.py">params</a>) -> <a href="./src/worqhat/types/flow_trigger_with_payload_response.py">FlowTriggerWithPayloadResponse</a></code>

# Client

## Storage

Types:

```python
from worqhat.types.client import (
    StorageDeleteFileByIDResponse,
    StorageRetrieveFileByIDResponse,
    StorageRetrieveFileByPathResponse,
    StorageUploadFileResponse,
)
```

Methods:

- <code title="delete /storage/delete/{fileId}">client.client.storage.<a href="./src/worqhat/resources/client/storage.py">delete_file_by_id</a>(file_id) -> <a href="./src/worqhat/types/client/storage_delete_file_by_id_response.py">StorageDeleteFileByIDResponse</a></code>
- <code title="get /storage/fetch/{fileId}">client.client.storage.<a href="./src/worqhat/resources/client/storage.py">retrieve_file_by_id</a>(file_id) -> <a href="./src/worqhat/types/client/storage_retrieve_file_by_id_response.py">StorageRetrieveFileByIDResponse</a></code>
- <code title="get /storage/fetch-by-path">client.client.storage.<a href="./src/worqhat/resources/client/storage.py">retrieve_file_by_path</a>(\*\*<a href="src/worqhat/types/client/storage_retrieve_file_by_path_params.py">params</a>) -> <a href="./src/worqhat/types/client/storage_retrieve_file_by_path_response.py">StorageRetrieveFileByPathResponse</a></code>
- <code title="post /storage/upload">client.client.storage.<a href="./src/worqhat/resources/client/storage.py">upload_file</a>(\*\*<a href="src/worqhat/types/client/storage_upload_file_params.py">params</a>) -> <a href="./src/worqhat/types/client/storage_upload_file_response.py">StorageUploadFileResponse</a></code>
