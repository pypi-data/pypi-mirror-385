# API Specification

## Overview

**API Name**: {{API_NAME}}
**Version**: {{API_VERSION}}
**Base URL**: {{API_BASE_URL}}
**Authentication**: {{AUTH_TYPE}}
**Last Updated**: {{CURRENT_DATE}}

## Authentication

### Method
{{AUTH_METHOD}} (JWT/OAuth2/API Key/Session)

### Headers
```http
Authorization: Bearer {{TOKEN}}
Content-Type: application/json
Accept: application/json
```

### Token Management
- **Expiry**: {{TOKEN_EXPIRY}}
- **Refresh**: {{REFRESH_ENDPOINT}}
- **Revocation**: {{REVOKE_ENDPOINT}}

## Endpoints

### {{RESOURCE_1}}

#### List {{RESOURCE_1}}s
```http
GET /api/{{RESOURCE_1_PATH}}
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | integer | No | Page number (default: 1) |
| pageSize | integer | No | Items per page (default: 20) |
| sort | string | No | Sort field (default: createdAt) |
| order | string | No | Sort order: asc\|desc |
| {{FILTER_1}} | {{TYPE}} | No | {{DESCRIPTION}} |

**Response:** 200 OK
```json
{
  "data": [
    {
      "id": "{{ID}}",
      "{{FIELD_1}}": "{{VALUE_1}}",
      "{{FIELD_2}}": "{{VALUE_2}}",
      "createdAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

#### Get {{RESOURCE_1}}
```http
GET /api/{{RESOURCE_1_PATH}}/:id
```

**Response:** 200 OK
```json
{
  "id": "{{ID}}",
  "{{FIELD_1}}": "{{VALUE_1}}",
  "{{FIELD_2}}": "{{VALUE_2}}",
  "createdAt": "2025-01-01T00:00:00Z",
  "updatedAt": "2025-01-01T00:00:00Z"
}
```

**Errors:**
- 404: {{RESOURCE_1}} not found

#### Create {{RESOURCE_1}}
```http
POST /api/{{RESOURCE_1_PATH}}
```

**Request Body:**
```json
{
  "{{FIELD_1}}": "{{VALUE_1}}",
  "{{FIELD_2}}": "{{VALUE_2}}"
}
```

**Validation Rules:**
| Field | Rules |
|-------|-------|
| {{FIELD_1}} | Required, {{RULES}} |
| {{FIELD_2}} | Optional, {{RULES}} |

**Response:** 201 Created
```json
{
  "id": "{{ID}}",
  "{{FIELD_1}}": "{{VALUE_1}}",
  "{{FIELD_2}}": "{{VALUE_2}}",
  "createdAt": "2025-01-01T00:00:00Z",
  "updatedAt": "2025-01-01T00:00:00Z"
}
```

**Errors:**
- 400: Validation error
- 409: {{RESOURCE_1}} already exists

#### Update {{RESOURCE_1}}
```http
PUT /api/{{RESOURCE_1_PATH}}/:id
PATCH /api/{{RESOURCE_1_PATH}}/:id
```

**Request Body:**
```json
{
  "{{FIELD_1}}": "{{NEW_VALUE_1}}",
  "{{FIELD_2}}": "{{NEW_VALUE_2}}"
}
```

**Response:** 200 OK
```json
{
  "id": "{{ID}}",
  "{{FIELD_1}}": "{{NEW_VALUE_1}}",
  "{{FIELD_2}}": "{{NEW_VALUE_2}}",
  "updatedAt": "2025-01-01T00:00:00Z"
}
```

**Errors:**
- 404: {{RESOURCE_1}} not found
- 400: Validation error

#### Delete {{RESOURCE_1}}
```http
DELETE /api/{{RESOURCE_1_PATH}}/:id
```

**Response:** 204 No Content

**Errors:**
- 404: {{RESOURCE_1}} not found

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "{{ERROR_CODE}}",
    "message": "{{ERROR_MESSAGE}}",
    "details": {
      "{{FIELD}}": ["{{VALIDATION_ERROR}}"]
    },
    "statusCode": 400
  }
}
```

### Error Codes
| Code | Status | Description |
|------|--------|-------------|
| VALIDATION_ERROR | 400 | Request validation failed |
| UNAUTHORIZED | 401 | Authentication required |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| CONFLICT | 409 | Resource conflict |
| RATE_LIMIT | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |

## Rate Limiting

- **Rate**: {{RATE_LIMIT}} requests per {{TIME_WINDOW}}
- **Headers:**
  - `X-RateLimit-Limit`: Maximum requests
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## Pagination

All list endpoints support pagination:
- `page`: Page number (1-indexed)
- `pageSize`: Items per page (max: {{MAX_PAGE_SIZE}})
- `total`: Total items
- `totalPages`: Total pages

## Filtering & Sorting

- **Filter**: `?{{FIELD}}={{VALUE}}`
- **Sort**: `?sort={{FIELD}}&order=asc|desc`
- **Search**: `?q={{SEARCH_TERM}}`

## Webhooks

### Events
| Event | Trigger |
|-------|---------|
| {{RESOURCE}}.created | {{RESOURCE}} created |
| {{RESOURCE}}.updated | {{RESOURCE}} updated |
| {{RESOURCE}}.deleted | {{RESOURCE}} deleted |

### Payload
```json
{
  "event": "{{RESOURCE}}.created",
  "timestamp": "2025-01-01T00:00:00Z",
  "data": { ... }
}
```

## Versioning

- **Current**: v{{VERSION}}
- **Header**: `Accept: application/vnd.{{API_NAME}}.v{{VERSION}}+json`
- **URL**: `/api/v{{VERSION}}/{{ENDPOINT}}`

---

**Maintainer**: {{MAINTAINER_NAME}}
**Documentation**: {{DOCS_URL}}
