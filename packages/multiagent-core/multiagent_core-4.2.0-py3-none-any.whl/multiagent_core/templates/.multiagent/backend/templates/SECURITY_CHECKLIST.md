# Security Checklist

## Authentication & Authorization

- [ ] Use secure authentication (JWT/OAuth2)
- [ ] Implement password hashing (bcrypt/argon2)
- [ ] Enforce strong password requirements
- [ ] Implement rate limiting on auth endpoints
- [ ] Use secure session management
- [ ] Implement RBAC (Role-Based Access Control)
- [ ] Use secure token storage
- [ ] Implement token refresh mechanism
- [ ] Add MFA (Multi-Factor Authentication)

## Input Validation

- [ ] Validate all user inputs
- [ ] Sanitize HTML inputs
- [ ] Use parameterized queries (prevent SQL injection)
- [ ] Validate file uploads
- [ ] Limit request payload size
- [ ] Validate content types
- [ ] Implement CSRF protection
- [ ] Use strict type checking

## API Security

- [ ] Use HTTPS only
- [ ] Implement CORS properly
- [ ] Add security headers (Helmet.js)
- [ ] Rate limit all endpoints
- [ ] Implement API versioning
- [ ] Use API keys for external access
- [ ] Log all API requests
- [ ] Implement request signing

## Data Protection

- [ ] Encrypt sensitive data at rest
- [ ] Use TLS for data in transit
- [ ] Never log sensitive data
- [ ] Implement data masking
- [ ] Regular database backups
- [ ] Secure backup storage
- [ ] Implement data retention policies
- [ ] PII data handling compliance

## Environment Security

- [ ] Store secrets in environment variables
- [ ] Use secret management (Vault/AWS Secrets Manager)
- [ ] Never commit secrets to git
- [ ] Rotate API keys regularly
- [ ] Use different keys per environment
- [ ] Implement least privilege access
- [ ] Regular security audits
- [ ] Dependency vulnerability scanning

## Error Handling

- [ ] Never expose stack traces
- [ ] Use generic error messages
- [ ] Log detailed errors securely
- [ ] Implement proper error codes
- [ ] Handle all edge cases
- [ ] Implement graceful degradation

## Security Headers

```typescript
app.use(helmet({
  contentSecurityPolicy: true,
  hsts: true,
  noSniff: true,
  xssFilter: true,
}));
```

## Rate Limiting

```typescript
app.use(rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
}));
```

---

**Security Contact**: {{SECURITY_EMAIL}}
**Last Review**: {{REVIEW_DATE}}
