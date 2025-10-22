# V1

Methods:

- <code title="get /api/v1/test-mongodb">client.v1.<a href="./src/studyfetch_sdk/resources/v1/v1.py">test_mongodb</a>() -> None</code>

## Folders

Types:

```python
from studyfetch_sdk.types.v1 import (
    FolderMetadata,
    FolderCreateResponse,
    FolderRetrieveResponse,
    FolderUpdateResponse,
    FolderListResponse,
    FolderGetTreeResponse,
    FolderListMaterialsResponse,
    FolderMoveResponse,
)
```

Methods:

- <code title="post /api/v1/folders">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">create</a>(\*\*<a href="src/studyfetch_sdk/types/v1/folder_create_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/folder_create_response.py">FolderCreateResponse</a></code>
- <code title="get /api/v1/folders/{id}">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">retrieve</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/folder_retrieve_response.py">FolderRetrieveResponse</a></code>
- <code title="patch /api/v1/folders/{id}">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">update</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/folder_update_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/folder_update_response.py">FolderUpdateResponse</a></code>
- <code title="get /api/v1/folders">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">list</a>(\*\*<a href="src/studyfetch_sdk/types/v1/folder_list_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/folder_list_response.py">FolderListResponse</a></code>
- <code title="delete /api/v1/folders/{id}">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">delete</a>(id) -> None</code>
- <code title="get /api/v1/folders/tree">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">get_tree</a>() -> <a href="./src/studyfetch_sdk/types/v1/folder_get_tree_response.py">FolderGetTreeResponse</a></code>
- <code title="get /api/v1/folders/{id}/materials">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">list_materials</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/folder_list_materials_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/folder_list_materials_response.py">FolderListMaterialsResponse</a></code>
- <code title="patch /api/v1/folders/{id}/move">client.v1.folders.<a href="./src/studyfetch_sdk/resources/v1/folders.py">move</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/folder_move_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/folder_move_response.py">FolderMoveResponse</a></code>

## Components

Types:

```python
from studyfetch_sdk.types.v1 import (
    ComponentResponse,
    ComponentListResponse,
    ComponentGenerateEmbedResponse,
)
```

Methods:

- <code title="post /api/v1/components">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">create</a>(\*\*<a href="src/studyfetch_sdk/types/v1/component_create_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/component_response.py">ComponentResponse</a></code>
- <code title="get /api/v1/components/{id}">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">retrieve</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/component_response.py">ComponentResponse</a></code>
- <code title="patch /api/v1/components/{id}">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">update</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/component_update_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/component_response.py">ComponentResponse</a></code>
- <code title="get /api/v1/components">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">list</a>(\*\*<a href="src/studyfetch_sdk/types/v1/component_list_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/component_list_response.py">ComponentListResponse</a></code>
- <code title="delete /api/v1/components/{id}">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">delete</a>(id) -> None</code>
- <code title="post /api/v1/components/{id}/activate">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">activate</a>(id) -> None</code>
- <code title="post /api/v1/components/{id}/deactivate">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">deactivate</a>(id) -> None</code>
- <code title="post /api/v1/components/{id}/embed">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">generate_embed</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/component_generate_embed_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/component_generate_embed_response.py">ComponentGenerateEmbedResponse</a></code>
- <code title="post /api/v1/components/{id}/interact">client.v1.components.<a href="./src/studyfetch_sdk/resources/v1/components.py">interact</a>(id) -> None</code>

## Usage

Methods:

- <code title="get /api/v1/usage/stats">client.v1.usage.<a href="./src/studyfetch_sdk/resources/v1/usage.py">get_stats</a>(\*\*<a href="src/studyfetch_sdk/types/v1/usage_get_stats_params.py">params</a>) -> None</code>
- <code title="get /api/v1/usage/summary">client.v1.usage.<a href="./src/studyfetch_sdk/resources/v1/usage.py">get_summary</a>(\*\*<a href="src/studyfetch_sdk/types/v1/usage_get_summary_params.py">params</a>) -> None</code>
- <code title="get /api/v1/usage/events">client.v1.usage.<a href="./src/studyfetch_sdk/resources/v1/usage.py">list_events</a>(\*\*<a href="src/studyfetch_sdk/types/v1/usage_list_events_params.py">params</a>) -> None</code>

## UsageAnalyst

Types:

```python
from studyfetch_sdk.types.v1 import UsageAnalystListChatMessagesResponse
```

Methods:

- <code title="get /api/v1/usage-analyst/test-questions">client.v1.usage_analyst.<a href="./src/studyfetch_sdk/resources/v1/usage_analyst.py">get_test_questions</a>(\*\*<a href="src/studyfetch_sdk/types/v1/usage_analyst_get_test_questions_params.py">params</a>) -> None</code>
- <code title="get /api/v1/usage-analyst/chat-messages">client.v1.usage_analyst.<a href="./src/studyfetch_sdk/resources/v1/usage_analyst.py">list_chat_messages</a>(\*\*<a href="src/studyfetch_sdk/types/v1/usage_analyst_list_chat_messages_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/usage_analyst_list_chat_messages_response.py">UsageAnalystListChatMessagesResponse</a></code>
- <code title="get /api/v1/usage-analyst/events">client.v1.usage_analyst.<a href="./src/studyfetch_sdk/resources/v1/usage_analyst.py">list_events</a>(\*\*<a href="src/studyfetch_sdk/types/v1/usage_analyst_list_events_params.py">params</a>) -> None</code>

## Embed

Methods:

- <code title="get /api/v1/embed/theme">client.v1.embed.<a href="./src/studyfetch_sdk/resources/v1/embed/embed.py">get_theme</a>(\*\*<a href="src/studyfetch_sdk/types/v1/embed_get_theme_params.py">params</a>) -> None</code>
- <code title="get /api/v1/embed/health">client.v1.embed.<a href="./src/studyfetch_sdk/resources/v1/embed/embed.py">health_check</a>() -> None</code>
- <code title="get /api/v1/embed/verify">client.v1.embed.<a href="./src/studyfetch_sdk/resources/v1/embed/embed.py">verify</a>(\*\*<a href="src/studyfetch_sdk/types/v1/embed_verify_params.py">params</a>) -> None</code>

### Component

Methods:

- <code title="get /api/v1/embed/component/{componentId}">client.v1.embed.component.<a href="./src/studyfetch_sdk/resources/v1/embed/component.py">retrieve</a>(component_id, \*\*<a href="src/studyfetch_sdk/types/v1/embed/component_retrieve_params.py">params</a>) -> None</code>
- <code title="post /api/v1/embed/component/{componentId}/interact">client.v1.embed.component.<a href="./src/studyfetch_sdk/resources/v1/embed/component.py">interact</a>(component_id, \*\*<a href="src/studyfetch_sdk/types/v1/embed/component_interact_params.py">params</a>) -> None</code>

### Context

Methods:

- <code title="get /api/v1/embed/context">client.v1.embed.context.<a href="./src/studyfetch_sdk/resources/v1/embed/context.py">retrieve</a>(\*\*<a href="src/studyfetch_sdk/types/v1/embed/context_retrieve_params.py">params</a>) -> None</code>
- <code title="post /api/v1/embed/context/clear">client.v1.embed.context.<a href="./src/studyfetch_sdk/resources/v1/embed/context.py">clear</a>(\*\*<a href="src/studyfetch_sdk/types/v1/embed/context_clear_params.py">params</a>) -> None</code>
- <code title="post /api/v1/embed/context/push">client.v1.embed.context.<a href="./src/studyfetch_sdk/resources/v1/embed/context.py">push</a>(\*\*<a href="src/studyfetch_sdk/types/v1/embed/context_push_params.py">params</a>) -> None</code>

## Chat

Methods:

- <code title="get /api/v1/chat/feedback">client.v1.chat.<a href="./src/studyfetch_sdk/resources/v1/chat.py">retrieve_feedback</a>(\*\*<a href="src/studyfetch_sdk/types/v1/chat_retrieve_feedback_params.py">params</a>) -> None</code>
- <code title="get /api/v1/chat/feedback/{feedbackId}/context">client.v1.chat.<a href="./src/studyfetch_sdk/resources/v1/chat.py">retrieve_feedback_context</a>(feedback_id) -> None</code>
- <code title="post /api/v1/chat/stream">client.v1.chat.<a href="./src/studyfetch_sdk/resources/v1/chat.py">stream</a>(\*\*<a href="src/studyfetch_sdk/types/v1/chat_stream_params.py">params</a>) -> None</code>

## ChatAnalytics

Types:

```python
from studyfetch_sdk.types.v1 import ChatAnalyticsResponse, ChatAnalyticsExportResponse
```

Methods:

- <code title="get /api/v1/chat-analytics/analyze">client.v1.chat_analytics.<a href="./src/studyfetch_sdk/resources/v1/chat_analytics.py">analyze</a>(\*\*<a href="src/studyfetch_sdk/types/v1/chat_analytics_analyze_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/chat_analytics_response.py">ChatAnalyticsResponse</a></code>
- <code title="get /api/v1/chat-analytics/export">client.v1.chat_analytics.<a href="./src/studyfetch_sdk/resources/v1/chat_analytics.py">export</a>(\*\*<a href="src/studyfetch_sdk/types/v1/chat_analytics_export_params.py">params</a>) -> str</code>
- <code title="get /api/v1/chat-analytics/component/{componentId}">client.v1.chat_analytics.<a href="./src/studyfetch_sdk/resources/v1/chat_analytics.py">get_component</a>(component_id, \*\*<a href="src/studyfetch_sdk/types/v1/chat_analytics_get_component_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/chat_analytics_response.py">ChatAnalyticsResponse</a></code>

## AssignmentGrader

Types:

```python
from studyfetch_sdk.types.v1 import (
    AssignmentGraderResponse,
    PerformanceItem,
    AssignmentGraderCreateResponse,
    AssignmentGraderGenerateReportResponse,
    AssignmentGraderGetAllResponse,
)
```

Methods:

- <code title="post /api/v1/assignment-grader/create">client.v1.assignment_grader.<a href="./src/studyfetch_sdk/resources/v1/assignment_grader/assignment_grader.py">create</a>(\*\*<a href="src/studyfetch_sdk/types/v1/assignment_grader_create_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/assignment_grader_create_response.py">AssignmentGraderCreateResponse</a></code>
- <code title="delete /api/v1/assignment-grader/delete/{id}">client.v1.assignment_grader.<a href="./src/studyfetch_sdk/resources/v1/assignment_grader/assignment_grader.py">delete</a>(id) -> None</code>
- <code title="get /api/v1/assignment-grader/educator-report/{assignmentId}">client.v1.assignment_grader.<a href="./src/studyfetch_sdk/resources/v1/assignment_grader/assignment_grader.py">generate_report</a>(assignment_id) -> <a href="./src/studyfetch_sdk/types/v1/assignment_grader_generate_report_response.py">AssignmentGraderGenerateReportResponse</a></code>
- <code title="get /api/v1/assignment-grader/get">client.v1.assignment_grader.<a href="./src/studyfetch_sdk/resources/v1/assignment_grader/assignment_grader.py">get_all</a>() -> <a href="./src/studyfetch_sdk/types/v1/assignment_grader_get_all_response.py">AssignmentGraderGetAllResponse</a></code>
- <code title="get /api/v1/assignment-grader/get/{id}">client.v1.assignment_grader.<a href="./src/studyfetch_sdk/resources/v1/assignment_grader/assignment_grader.py">get_by_id</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/assignment_grader_response.py">AssignmentGraderResponse</a></code>

### RubricTemplates

Types:

```python
from studyfetch_sdk.types.v1.assignment_grader import (
    RubricCriterion,
    RubricTemplateResponse,
    RubricTemplateListResponse,
)
```

Methods:

- <code title="post /api/v1/assignment-grader/rubric-templates">client.v1.assignment_grader.rubric_templates.<a href="./src/studyfetch_sdk/resources/v1/assignment_grader/rubric_templates.py">create</a>(\*\*<a href="src/studyfetch_sdk/types/v1/assignment_grader/rubric_template_create_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/assignment_grader/rubric_template_response.py">RubricTemplateResponse</a></code>
- <code title="get /api/v1/assignment-grader/rubric-templates">client.v1.assignment_grader.rubric_templates.<a href="./src/studyfetch_sdk/resources/v1/assignment_grader/rubric_templates.py">list</a>() -> <a href="./src/studyfetch_sdk/types/v1/assignment_grader/rubric_template_list_response.py">RubricTemplateListResponse</a></code>
- <code title="delete /api/v1/assignment-grader/rubric-templates/{id}">client.v1.assignment_grader.rubric_templates.<a href="./src/studyfetch_sdk/resources/v1/assignment_grader/rubric_templates.py">delete</a>(id) -> None</code>
- <code title="get /api/v1/assignment-grader/rubric-templates/{id}">client.v1.assignment_grader.rubric_templates.<a href="./src/studyfetch_sdk/resources/v1/assignment_grader/rubric_templates.py">get_by_id</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/assignment_grader/rubric_template_response.py">RubricTemplateResponse</a></code>

## Materials

Types:

```python
from studyfetch_sdk.types.v1 import (
    Content,
    GeneratedMaterialResponse,
    MaterialResponse,
    Reference,
    MaterialListResponse,
    MaterialCancelJobResponse,
    MaterialCreateBatchUploadURLsResponse,
    MaterialGetDebugInfoResponse,
    MaterialGetDownloadURLResponse,
    MaterialGetJobStatusResponse,
    MaterialSearchResponse,
)
```

Methods:

- <code title="post /api/v1/materials">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">create</a>(\*\*<a href="src/studyfetch_sdk/types/v1/material_create_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_response.py">MaterialResponse</a></code>
- <code title="get /api/v1/materials/{id}">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">retrieve</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/material_response.py">MaterialResponse</a></code>
- <code title="patch /api/v1/materials/{id}">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">update</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/material_update_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_response.py">MaterialResponse</a></code>
- <code title="get /api/v1/materials">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">list</a>(\*\*<a href="src/studyfetch_sdk/types/v1/material_list_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_list_response.py">MaterialListResponse</a></code>
- <code title="delete /api/v1/materials/{id}">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">delete</a>(id) -> None</code>
- <code title="post /api/v1/materials/{id}/cancel-job">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">cancel_job</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/material_cancel_job_response.py">MaterialCancelJobResponse</a></code>
- <code title="post /api/v1/materials/upload-and-process">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">create_and_process</a>(\*\*<a href="src/studyfetch_sdk/types/v1/material_create_and_process_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_response.py">MaterialResponse</a></code>
- <code title="post /api/v1/materials/batch">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">create_batch_upload_urls</a>(\*\*<a href="src/studyfetch_sdk/types/v1/material_create_batch_upload_urls_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_create_batch_upload_urls_response.py">MaterialCreateBatchUploadURLsResponse</a></code>
- <code title="post /api/v1/materials/generate">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">generate</a>(\*\*<a href="src/studyfetch_sdk/types/v1/material_generate_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/generated_material_response.py">GeneratedMaterialResponse</a></code>
- <code title="post /api/v1/materials/generate-and-process">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">generate_and_process</a>(\*\*<a href="src/studyfetch_sdk/types/v1/material_generate_and_process_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/generated_material_response.py">GeneratedMaterialResponse</a></code>
- <code title="get /api/v1/materials/{id}/debug">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">get_debug_info</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/material_get_debug_info_response.py">MaterialGetDebugInfoResponse</a></code>
- <code title="get /api/v1/materials/{id}/download-url">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">get_download_url</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/material_get_download_url_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_get_download_url_response.py">MaterialGetDownloadURLResponse</a></code>
- <code title="get /api/v1/materials/{id}/job-status">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">get_job_status</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/material_get_job_status_response.py">MaterialGetJobStatusResponse</a></code>
- <code title="post /api/v1/materials/{id}/move">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">move</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/material_move_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_response.py">MaterialResponse</a></code>
- <code title="post /api/v1/materials/{id}/rename">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">rename</a>(id, \*\*<a href="src/studyfetch_sdk/types/v1/material_rename_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_response.py">MaterialResponse</a></code>
- <code title="post /api/v1/materials/{id}/reprocess">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">reprocess</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/material_response.py">MaterialResponse</a></code>
- <code title="post /api/v1/materials/search">client.v1.materials.<a href="./src/studyfetch_sdk/resources/v1/materials/materials.py">search</a>(\*\*<a href="src/studyfetch_sdk/types/v1/material_search_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_search_response.py">MaterialSearchResponse</a></code>

### Upload

Types:

```python
from studyfetch_sdk.types.v1.materials import UploadGetPresignedURLResponse
```

Methods:

- <code title="post /api/v1/materials/upload/complete">client.v1.materials.upload.<a href="./src/studyfetch_sdk/resources/v1/materials/upload.py">complete_upload</a>(\*\*<a href="src/studyfetch_sdk/types/v1/materials/upload_complete_upload_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_response.py">MaterialResponse</a></code>
- <code title="post /api/v1/materials/upload/presigned-url">client.v1.materials.upload.<a href="./src/studyfetch_sdk/resources/v1/materials/upload.py">get_presigned_url</a>(\*\*<a href="src/studyfetch_sdk/types/v1/materials/upload_get_presigned_url_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/materials/upload_get_presigned_url_response.py">UploadGetPresignedURLResponse</a></code>
- <code title="post /api/v1/materials/upload">client.v1.materials.upload.<a href="./src/studyfetch_sdk/resources/v1/materials/upload.py">upload_file</a>(\*\*<a href="src/studyfetch_sdk/types/v1/materials/upload_upload_file_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_response.py">MaterialResponse</a></code>
- <code title="post /api/v1/materials/upload/file-and-process">client.v1.materials.upload.<a href="./src/studyfetch_sdk/resources/v1/materials/upload.py">upload_file_and_process</a>(\*\*<a href="src/studyfetch_sdk/types/v1/materials/upload_upload_file_and_process_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_response.py">MaterialResponse</a></code>
- <code title="post /api/v1/materials/upload/url">client.v1.materials.upload.<a href="./src/studyfetch_sdk/resources/v1/materials/upload.py">upload_from_url</a>(\*\*<a href="src/studyfetch_sdk/types/v1/materials/upload_upload_from_url_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_response.py">MaterialResponse</a></code>
- <code title="post /api/v1/materials/upload/url-and-process">client.v1.materials.upload.<a href="./src/studyfetch_sdk/resources/v1/materials/upload.py">upload_from_url_and_process</a>(\*\*<a href="src/studyfetch_sdk/types/v1/materials/upload_upload_from_url_and_process_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/material_response.py">MaterialResponse</a></code>

### Bulk

Types:

```python
from studyfetch_sdk.types.v1.materials import BulkMoveResponse
```

Methods:

- <code title="post /api/v1/materials/bulk/move">client.v1.materials.bulk.<a href="./src/studyfetch_sdk/resources/v1/materials/bulk.py">move</a>(\*\*<a href="src/studyfetch_sdk/types/v1/materials/bulk_move_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/materials/bulk_move_response.py">BulkMoveResponse</a></code>

## PdfGenerator

Types:

```python
from studyfetch_sdk.types.v1 import (
    PdfGeneratorCreateResponse,
    PdfGeneratorDeleteResponse,
    PdfGeneratorGetAllResponse,
)
```

Methods:

- <code title="post /api/v1/pdf-generator/create">client.v1.pdf_generator.<a href="./src/studyfetch_sdk/resources/v1/pdf_generator/pdf_generator.py">create</a>(\*\*<a href="src/studyfetch_sdk/types/v1/pdf_generator_create_params.py">params</a>) -> <a href="./src/studyfetch_sdk/types/v1/pdf_generator_create_response.py">PdfGeneratorCreateResponse</a></code>
- <code title="delete /api/v1/pdf-generator/delete/{id}">client.v1.pdf_generator.<a href="./src/studyfetch_sdk/resources/v1/pdf_generator/pdf_generator.py">delete</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/pdf_generator_delete_response.py">PdfGeneratorDeleteResponse</a></code>
- <code title="get /api/v1/pdf-generator/get">client.v1.pdf_generator.<a href="./src/studyfetch_sdk/resources/v1/pdf_generator/pdf_generator.py">get_all</a>() -> <a href="./src/studyfetch_sdk/types/v1/pdf_generator_get_all_response.py">PdfGeneratorGetAllResponse</a></code>
- <code title="get /api/v1/pdf-generator/get/{id}">client.v1.pdf_generator.<a href="./src/studyfetch_sdk/resources/v1/pdf_generator/pdf_generator.py">get_by_id</a>(id) -> <a href="./src/studyfetch_sdk/types/v1/pdf_generator/pdf_response.py">PdfResponse</a></code>

### Get

Types:

```python
from studyfetch_sdk.types.v1.pdf_generator import PdfResponse
```
