# Routing Architecture

## File-Based Routing (Next.js)

```
app/
├── page.tsx              → /
├── about/page.tsx        → /about
├── blog/
│   ├── page.tsx          → /blog
│   └── [slug]/page.tsx   → /blog/:slug
└── api/
    └── users/route.ts    → /api/users
```

## React Router Setup

```typescript
const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      { path: 'about', element: <About /> },
      { path: 'users/:id', element: <UserDetail /> },
    ],
  },
]);
```

## Protected Routes

```typescript
function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" />;
  return <>{children}</>;
}

<Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
```

## URL State Management

```typescript
const [searchParams, setSearchParams] = useSearchParams();

// Read
const page = searchParams.get('page') || '1';

// Write
setSearchParams({ page: '2', sort: 'name' });
```

---

See also: [Component Patterns](./component-patterns.md)
