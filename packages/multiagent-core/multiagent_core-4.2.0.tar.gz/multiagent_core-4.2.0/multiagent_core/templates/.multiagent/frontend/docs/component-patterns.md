# Component Patterns

## Container/Presentational Pattern

**Container**: Logic, state, data fetching
**Presentational**: Pure UI, props only

```typescript
// Container
export function UserListContainer() {
  const { data, isLoading } = useUsers();
  return <UserList users={data} loading={isLoading} />;
}

// Presentational
export function UserList({ users, loading }: Props) {
  if (loading) return <Skeleton />;
  return <ul>{users.map(user => <UserItem key={user.id} user={user} />)}</ul>;
}
```

## Compound Components

```typescript
<Select value={value} onChange={onChange}>
  <Select.Trigger />
  <Select.Options>
    <Select.Option value="1">Option 1</Select.Option>
  </Select.Options>
</Select>
```

## Render Props

```typescript
<DataFetcher url="/api/users">
  {({ data, loading }) => (
    loading ? <Spinner /> : <UserList users={data} />
  )}
</DataFetcher>
```

## Higher-Order Components

```typescript
const withAuth = (Component) => (props) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Redirect to="/login" />;
  return <Component {...props} />;
};
```

## Custom Hooks Pattern

```typescript
function useUserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchUsers().then(setUsers).finally(() => setLoading(false));
  }, []);
  
  return { users, loading };
}
```

---

See also: [State Management](./state-management.md), [Routing](./routing-architecture.md)
