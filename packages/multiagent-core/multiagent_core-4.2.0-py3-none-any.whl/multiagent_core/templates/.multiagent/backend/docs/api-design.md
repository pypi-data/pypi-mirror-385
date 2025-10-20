# API Design Principles

## RESTful Conventions

| Method | Purpose | Example |
|--------|---------|---------|
| GET | Retrieve | GET /users |
| POST | Create | POST /users |
| PUT | Replace | PUT /users/:id |
| PATCH | Update | PATCH /users/:id |
| DELETE | Delete | DELETE /users/:id |

## URL Structure

```
/api/v1/resources
/api/v1/resources/:id
/api/v1/resources/:id/subresources
```

## Response Format

```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2025-01-01T00:00:00Z",
    "version": "1.0"
  }
}
```

## Pagination

```
GET /users?page=1&pageSize=20&sort=createdAt&order=desc
```

## Error Handling

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": {
      "email": ["Must be valid email"]
    }
  }
}
```

## Versioning

- URL: `/api/v1/users`
- Header: `Accept: application/vnd.api+json;version=1`

---

See also: [Authentication](./authentication.md), [Database Patterns](./database-patterns.md)
