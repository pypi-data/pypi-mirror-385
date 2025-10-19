# Authentication Patterns

## JWT Authentication

```typescript
// Generate token
const token = jwt.sign({ userId: user.id }, SECRET, { expiresIn: '7d' });

// Verify token
const decoded = jwt.verify(token, SECRET);

// Middleware
async function authMiddleware(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Unauthorized' });
  
  try {
    req.user = jwt.verify(token, SECRET);
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
}
```

## Password Hashing

```typescript
import bcrypt from 'bcrypt';

// Hash password
const hashedPassword = await bcrypt.hash(password, 10);

// Verify password
const isValid = await bcrypt.compare(password, hashedPassword);
```

## OAuth2 Flow

1. Redirect to provider: `GET /auth/google`
2. Provider redirects back: `GET /auth/google/callback?code=...`
3. Exchange code for token
4. Create/update user
5. Return JWT

## Role-Based Access Control

```typescript
function requireRole(...roles: string[]) {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Forbidden' });
    }
    next();
  };
}

// Usage
app.get('/admin', authMiddleware, requireRole('admin'), adminHandler);
```

## Session Management

```typescript
// Store session
await redis.set(`session:${sessionId}`, JSON.stringify(user), 'EX', 3600);

// Get session
const user = JSON.parse(await redis.get(`session:${sessionId}`));

// Delete session
await redis.del(`session:${sessionId}`);
```

---

See also: [Security Checklist](../templates/SECURITY_CHECKLIST.md), [API Design](./api-design.md)
