# Database Patterns

## Repository Pattern

```typescript
class UserRepository {
  async findById(id: string): Promise<User | null> {
    return db.user.findUnique({ where: { id } });
  }

  async findAll(params: QueryParams): Promise<User[]> {
    return db.user.findMany({
      where: params.filter,
      orderBy: params.sort,
      skip: params.offset,
      take: params.limit,
    });
  }
}
```

## Transactions

```typescript
await db.$transaction(async (tx) => {
  const user = await tx.user.create({ data: userData });
  await tx.profile.create({ data: { userId: user.id, ...profileData } });
});
```

## Migrations

```sql
-- migrations/001_create_users.sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Indexing Strategy

- Primary keys: Automatic
- Foreign keys: Always indexed
- Frequently queried columns: Add index
- Composite indexes for multi-column queries

## Query Optimization

```typescript
// ❌ N+1 Problem
for (const user of users) {
  user.posts = await db.post.findMany({ where: { userId: user.id } });
}

// ✅ Solution: Include relations
const users = await db.user.findMany({
  include: { posts: true }
});
```

---

See also: [Service Architecture](../templates/SERVICE_ARCHITECTURE.md), [Database Schema](../templates/DATABASE_SCHEMA.md)
