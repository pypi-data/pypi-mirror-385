# Applications

Types:

```python
from gizmo_sdk.types import (
    LoanPurpose,
    Milestone,
    State,
    ApplicationCreateResponse,
    ApplicationRetrieveResponse,
    ApplicationUpdateResponse,
)
```

Methods:

- <code title="post /applications">client.applications.<a href="./src/gizmo_sdk/resources/applications.py">create</a>(\*\*<a href="src/gizmo_sdk/types/application_create_params.py">params</a>) -> <a href="./src/gizmo_sdk/types/application_create_response.py">ApplicationCreateResponse</a></code>
- <code title="get /applications/{id}">client.applications.<a href="./src/gizmo_sdk/resources/applications.py">retrieve</a>(id) -> <a href="./src/gizmo_sdk/types/application_retrieve_response.py">ApplicationRetrieveResponse</a></code>
- <code title="patch /applications/{id}">client.applications.<a href="./src/gizmo_sdk/resources/applications.py">update</a>(id, \*\*<a href="src/gizmo_sdk/types/application_update_params.py">params</a>) -> <a href="./src/gizmo_sdk/types/application_update_response.py">Optional[ApplicationUpdateResponse]</a></code>
