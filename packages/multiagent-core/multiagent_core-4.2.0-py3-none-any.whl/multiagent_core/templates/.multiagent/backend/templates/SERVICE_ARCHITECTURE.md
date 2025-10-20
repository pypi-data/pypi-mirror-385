# Service Architecture

## Overview

**Architecture**: {{ARCHITECTURE_TYPE}} (Monolithic/Microservices/Serverless)
**Framework**: {{FRAMEWORK}} (Express/Fastify/NestJS/FastAPI/Django)
**Language**: {{LANGUAGE}}
**Version**: {{VERSION}}

## Layer Architecture

```
┌─────────────────────────────────────┐
│       API Layer (Controllers)       │
│  - Route handlers                   │
│  - Request validation               │
│  - Response formatting              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│       Service Layer (Business)      │
│  - Business logic                   │
│  - Data transformation              │
│  - Transaction management           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Repository Layer (Data Access)   │
│  - Database queries                 │
│  - Data mapping                     │
│  - Cache management                 │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│         Data Layer (Models)         │
│  - Database schema                  │
│  - Data validation                  │
└─────────────────────────────────────┘
```

## Directory Structure

```
src/
├── controllers/        # API route handlers
│   ├── {{RESOURCE_1}}.controller.ts
│   └── {{RESOURCE_2}}.controller.ts
├── services/          # Business logic
│   ├── {{RESOURCE_1}}.service.ts
│   └── {{RESOURCE_2}}.service.ts
├── repositories/      # Data access
│   ├── {{RESOURCE_1}}.repository.ts
│   └── {{RESOURCE_2}}.repository.ts
├── models/            # Data models
│   ├── {{RESOURCE_1}}.model.ts
│   └── {{RESOURCE_2}}.model.ts
├── middleware/        # Express middleware
│   ├── auth.middleware.ts
│   ├── validation.middleware.ts
│   └── error.middleware.ts
├── utils/             # Utilities
│   ├── logger.ts
│   └── helpers.ts
└── config/            # Configuration
    ├── database.ts
    └── environment.ts
```

## Controllers

### Example Controller
```typescript
// src/controllers/{{RESOURCE}}.controller.ts
export class {{RESOURCE}}Controller {
  constructor(private {{RESOURCE}}Service: {{RESOURCE}}Service) {}

  async list(req: Request, res: Response) {
    const items = await this.{{RESOURCE}}Service.list(req.query);
    res.json({ data: items });
  }

  async get(req: Request, res: Response) {
    const item = await this.{{RESOURCE}}Service.get(req.params.id);
    res.json(item);
  }

  async create(req: Request, res: Response) {
    const item = await this.{{RESOURCE}}Service.create(req.body);
    res.status(201).json(item);
  }

  async update(req: Request, res: Response) {
    const item = await this.{{RESOURCE}}Service.update(req.params.id, req.body);
    res.json(item);
  }

  async delete(req: Request, res: Response) {
    await this.{{RESOURCE}}Service.delete(req.params.id);
    res.status(204).send();
  }
}
```

## Services

### Example Service
```typescript
// src/services/{{RESOURCE}}.service.ts
export class {{RESOURCE}}Service {
  constructor(private repository: {{RESOURCE}}Repository) {}

  async list(params: QueryParams) {
    return this.repository.findAll(params);
  }

  async get(id: string) {
    const item = await this.repository.findById(id);
    if (!item) throw new NotFoundError('{{RESOURCE}} not found');
    return item;
  }

  async create(data: Create{{RESOURCE}}DTO) {
    // Business logic
    return this.repository.create(data);
  }

  async update(id: string, data: Update{{RESOURCE}}DTO) {
    await this.get(id); // Check exists
    return this.repository.update(id, data);
  }

  async delete(id: string) {
    await this.get(id); // Check exists
    return this.repository.delete(id);
  }
}
```

## Repositories

### Example Repository
```typescript
// src/repositories/{{RESOURCE}}.repository.ts
export class {{RESOURCE}}Repository {
  async findAll(params: QueryParams) {
    return db.{{TABLE}}.findMany({
      where: params.filter,
      orderBy: params.sort,
      skip: params.offset,
      take: params.limit,
    });
  }

  async findById(id: string) {
    return db.{{TABLE}}.findUnique({ where: { id } });
  }

  async create(data: any) {
    return db.{{TABLE}}.create({ data });
  }

  async update(id: string, data: any) {
    return db.{{TABLE}}.update({ where: { id }, data });
  }

  async delete(id: string) {
    return db.{{TABLE}}.delete({ where: { id } });
  }
}
```

## Dependency Injection

```typescript
// src/container.ts
import { Container } from 'inversify';

const container = new Container();

container.bind({{RESOURCE}}Repository).toSelf();
container.bind({{RESOURCE}}Service).toSelf();
container.bind({{RESOURCE}}Controller).toSelf();

export { container };
```

## Error Handling

```typescript
// src/middleware/error.middleware.ts
export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) {
  if (err instanceof ValidationError) {
    return res.status(400).json({
      error: { code: 'VALIDATION_ERROR', message: err.message }
    });
  }

  if (err instanceof NotFoundError) {
    return res.status(404).json({
      error: { code: 'NOT_FOUND', message: err.message }
    });
  }

  logger.error(err);
  res.status(500).json({
    error: { code: 'INTERNAL_ERROR', message: 'Internal server error' }
  });
}
```

---

**Maintainer**: {{MAINTAINER_NAME}}
