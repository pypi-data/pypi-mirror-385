# Database Schema

## Overview

**Database**: {{DATABASE_TYPE}} (PostgreSQL/MySQL/MongoDB)
**Version**: {{DB_VERSION}}
**Schema Version**: {{SCHEMA_VERSION}}
**Last Updated**: {{CURRENT_DATE}}

## Entity Relationship Diagram

```
{{TABLE_1}} ─────┐
  │             │
  │             ▼
  │         {{TABLE_2}}
  │             │
  ▼             ▼
{{TABLE_3}} ◄─ {{TABLE_4}}
```

## Tables

### {{TABLE_1}}

**Purpose**: {{PURPOSE}}

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID/SERIAL | PRIMARY KEY | Unique identifier |
| {{FIELD_1}} | {{TYPE_1}} | NOT NULL | {{DESC_1}} |
| {{FIELD_2}} | {{TYPE_2}} | UNIQUE | {{DESC_2}} |
| {{FIELD_3}} | {{TYPE_3}} | | {{DESC_3}} |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update |

**Indexes:**
- `idx_{{TABLE_1}}_{{FIELD}}` on `{{FIELD}}`
- `idx_{{TABLE_1}}_created` on `created_at DESC`

**Foreign Keys:**
- `{{FK_NAME}}`: {{FIELD}} REFERENCES {{OTHER_TABLE}}(id) ON DELETE {{CASCADE/SET NULL}}

### {{TABLE_2}}

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| {{FIELD_1}} | {{TYPE_1}} | NOT NULL | {{DESC_1}} |
| {{FK_FIELD}} | UUID | FOREIGN KEY | References {{TABLE_1}} |
| created_at | TIMESTAMP | NOT NULL | Creation time |

## Relationships

### One-to-Many
- {{TABLE_1}} → {{TABLE_2}} (one {{TABLE_1}} has many {{TABLE_2}}s)

### Many-to-Many
- {{TABLE_1}} ↔ {{TABLE_2}} through {{JOIN_TABLE}}

### One-to-One
- {{TABLE_1}} → {{TABLE_2}} (one-to-one relationship)

## Migrations

### Version {{VERSION}}
```sql
-- Create {{TABLE_1}}
CREATE TABLE {{TABLE_1}} (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  {{FIELD_1}} {{TYPE_1}} NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_{{TABLE_1}}_{{FIELD}} ON {{TABLE_1}}({{FIELD}});

-- Create trigger for updated_at
CREATE TRIGGER update_{{TABLE_1}}_updated_at
  BEFORE UPDATE ON {{TABLE_1}}
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Queries

### Common Queries
```sql
-- List with pagination
SELECT * FROM {{TABLE_1}}
ORDER BY created_at DESC
LIMIT {{PAGE_SIZE}} OFFSET {{OFFSET}};

-- Get with relations
SELECT t1.*, t2.{{FIELD}}
FROM {{TABLE_1}} t1
LEFT JOIN {{TABLE_2}} t2 ON t1.id = t2.{{FK_FIELD}}
WHERE t1.id = $1;
```

## Performance

### Optimization Strategies
- Indexes on frequently queried columns
- Composite indexes for multi-column queries
- Partitioning for large tables
- Materialized views for complex queries

---

**Maintainer**: {{MAINTAINER_NAME}}
