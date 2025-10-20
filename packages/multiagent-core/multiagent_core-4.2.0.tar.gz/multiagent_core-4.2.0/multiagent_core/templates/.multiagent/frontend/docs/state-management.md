# State Management Guide

## When to Use What

| State Type | Tool | Example |
|------------|------|---------|
| Server data | React Query | API responses |
| Global UI | Zustand/Redux | Theme, sidebar open |
| Component | useState | Form inputs, toggles |
| URL | Router | Filters, page number |
| Form | React Hook Form | Multi-step forms |

## React Query for Server State

```typescript
// Queries
const { data, isLoading, error } = useQuery({
  queryKey: ['users', params],
  queryFn: () => fetchUsers(params),
});

// Mutations
const mutation = useMutation({
  mutationFn: createUser,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['users'] });
  },
});
```

## Zustand for Global State

```typescript
const useStore = create((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null }),
}));

// Usage
const { user, setUser } = useStore();
```

## Form State with React Hook Form

```typescript
const { register, handleSubmit, formState: { errors } } = useForm();

<input {...register('email', { required: true, pattern: /^\S+@\S+$/ })} />
{errors.email && <span>Invalid email</span>}
```

---

See also: [API Client](../templates/API_CLIENT.md), [State Architecture](../templates/STATE_ARCHITECTURE.md)
