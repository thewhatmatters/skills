# Component Patterns Reference

Architecture patterns, layout strategies, state management, and anti-patterns for React/Next.js frontend development.

## Table of Contents

-   [Component Architecture](#component-architecture)
-   [Layout Patterns](#layout-patterns)
-   [State Management](#state-management)
-   [Performance Patterns](#performance-patterns)
-   [TypeScript Patterns](#typescript-patterns)
-   [Anti-Patterns](#anti-patterns)

## Component Architecture

### Component Hierarchy

```
src/
├── components/
│   ├── ui/              # shadcn primitives (don't modify)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── ...
│   ├── common/          # Shared, generic components
│   │   ├── loading-button.tsx
│   │   ├── data-table.tsx
│   │   └── stat-card.tsx
│   ├── features/        # Feature-specific components
│   │   ├── auth/
│   │   │   ├── login-form.tsx
│   │   │   └── signup-form.tsx
│   │   └── dashboard/
│   │       ├── metrics-grid.tsx
│   │       └── recent-activity.tsx
│   └── layout/          # Layout components
│       ├── header.tsx
│       ├── sidebar.tsx
│       └── footer.tsx
├── hooks/               # Custom hooks
├── lib/                 # Utilities (cn, api clients)
└── types/               # Shared TypeScript types
```

### Component Size Guidelines

| Lines   | Recommendation            |
| ------- | ------------------------- |
| < 50    | Single file, good size    |
| 50-150  | Consider extracting hooks |
| 150-300 | Split into subcomponents  |
| > 300   | Definitely refactor       |

### Single Responsibility

```tsx
// ❌ Does too much
function UserDashboard() {
    // Fetches data
    // Handles auth
    // Renders multiple complex sections
    // Manages local state
    // Has side effects
}

// ✅ Separated concerns
function UserDashboard() {
    return (
        <DashboardLayout>
            <DashboardHeader />
            <MetricsSection />
            <RecentActivitySection />
        </DashboardLayout>
    );
}

function MetricsSection() {
    const { data, isLoading } = useMetrics();

    if (isLoading) return <MetricsSkeleton />;

    return <MetricsGrid data={data} />;
}
```

### Composition Over Props

```tsx
// ❌ Prop explosion
<Card
  title="Title"
  description="Description"
  headerIcon={<Icon />}
  headerAction={<Button>Action</Button>}
  footerLeft={<Text>Left</Text>}
  footerRight={<Button>Right</Button>}
  bordered
  elevated
/>

// ✅ Composition
<Card>
  <CardHeader>
    <CardIcon><Icon /></CardIcon>
    <div>
      <CardTitle>Title</CardTitle>
      <CardDescription>Description</CardDescription>
    </div>
    <CardAction><Button>Action</Button></CardAction>
  </CardHeader>
  <CardContent>
    {/* Content */}
  </CardContent>
  <CardFooter>
    <Text>Left</Text>
    <Button>Right</Button>
  </CardFooter>
</Card>
```

### Container/Presenter Pattern

```tsx
// Container (handles data and logic)
function UserListContainer() {
    const { data: users, isLoading, error } = useUsers();
    const [searchTerm, setSearchTerm] = useState("");

    const filteredUsers = useMemo(
        () =>
            users?.filter((user) =>
                user.name.toLowerCase().includes(searchTerm.toLowerCase())
            ) ?? [],
        [users, searchTerm]
    );

    if (error) return <ErrorState error={error} />;

    return (
        <UserList
            users={filteredUsers}
            isLoading={isLoading}
            searchTerm={searchTerm}
            onSearchChange={setSearchTerm}
        />
    );
}

// Presenter (pure rendering)
interface UserListProps {
    users: User[];
    isLoading: boolean;
    searchTerm: string;
    onSearchChange: (term: string) => void;
}

function UserList({
    users,
    isLoading,
    searchTerm,
    onSearchChange,
}: UserListProps) {
    return (
        <div>
            <SearchInput value={searchTerm} onChange={onSearchChange} />
            {isLoading ? (
                <UserListSkeleton />
            ) : (
                <ul>
                    {users.map((user) => (
                        <UserListItem key={user.id} user={user} />
                    ))}
                </ul>
            )}
        </div>
    );
}
```

## Layout Patterns

### App Shell

```tsx
// app/layout.tsx
export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <body>
                <div className="flex min-h-screen flex-col">
                    <Header className="sticky top-0 z-50" />
                    <div className="flex flex-1">
                        <Sidebar className="hidden w-64 lg:block" />
                        <main className="flex-1 p-6">{children}</main>
                    </div>
                    <Footer />
                </div>
            </body>
        </html>
    );
}
```

### Responsive Grid

```tsx
// Auto-fit grid (columns based on available space)
<div className="grid grid-cols-[repeat(auto-fit,minmax(280px,1fr))] gap-6">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>

// Fixed responsive grid
<div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
  {items.map(item => <Card key={item.id} {...item} />)}
</div>

// Dashboard grid with different sizes
<div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
  <StatCard className="lg:col-span-2" />
  <StatCard />
  <StatCard />
  <ChartCard className="md:col-span-2 lg:col-span-3" />
  <ActivityFeed className="md:col-span-2 lg:col-span-1 lg:row-span-2" />
</div>
```

### Sticky Elements

```tsx
// Sticky header
<header className="sticky top-0 z-40 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
  <nav className="container flex h-16 items-center">
    {/* Nav content */}
  </nav>
</header>

// Sticky sidebar
<aside className="sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto border-r">
  {/* Sidebar content */}
</aside>

// Sticky table header
<div className="overflow-auto">
  <table>
    <thead className="sticky top-0 bg-background">
      {/* Headers */}
    </thead>
    <tbody>{/* Rows */}</tbody>
  </table>
</div>
```

### Content Width Patterns

```tsx
// Full width with max constraint
<div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
  {children}
</div>

// Prose width for readability
<article className="prose prose-lg mx-auto max-w-prose">
  {content}
</article>

// Wide content area
<div className="container">
  <div className="mx-auto max-w-4xl">
    {children}
  </div>
</div>
```

## State Management

### State Location Decision Tree

```
Is the state needed by multiple components?
├── No → useState in the component
└── Yes → Is it needed by siblings?
          ├── No → useState in nearest common ancestor
          └── Yes → Is it global app state?
                    ├── No → Context or prop drilling
                    └── Yes → Global store (Zustand, Jotai)
```

### Local State

```tsx
function SearchableList({ items }: { items: Item[] }) {
  // UI state - local
  const [searchTerm, setSearchTerm] = useState("");
  const [isExpanded, setIsExpanded] = useState(false);

  // Derived state - no useState needed
  const filteredItems = useMemo(
    () => items.filter(item => item.name.includes(searchTerm)),
    [items, searchTerm]
  );

  return (/* ... */);
}
```

### Lifted State

```tsx
// Parent manages state, children receive via props
function ProductPage() {
    const [selectedVariant, setSelectedVariant] = useState<Variant | null>(
        null
    );

    return (
        <div className="grid gap-8 lg:grid-cols-2">
            <ProductGallery variant={selectedVariant} />
            <ProductInfo
                variant={selectedVariant}
                onVariantChange={setSelectedVariant}
            />
        </div>
    );
}
```

### Context for Shared State

```tsx
// contexts/theme-context.tsx
interface ThemeContextType {
    theme: "light" | "dark";
    toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
    const [theme, setTheme] = useState<"light" | "dark">("light");

    const toggleTheme = useCallback(() => {
        setTheme((prev) => (prev === "light" ? "dark" : "light"));
    }, []);

    return (
        <ThemeContext.Provider value={{ theme, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}

export function useTheme() {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error("useTheme must be used within ThemeProvider");
    }
    return context;
}
```

### Server State (React Query / SWR)

```tsx
// Use React Query for server state
function UserProfile({ userId }: { userId: string }) {
    const {
        data: user,
        isLoading,
        error,
    } = useQuery({
        queryKey: ["user", userId],
        queryFn: () => fetchUser(userId),
        staleTime: 5 * 60 * 1000, // 5 minutes
    });

    if (isLoading) return <ProfileSkeleton />;
    if (error) return <ErrorState error={error} />;

    return <ProfileCard user={user} />;
}
```

## Performance Patterns

### Memoization

```tsx
// useMemo for expensive computations
const sortedItems = useMemo(() => {
    return [...items].sort((a, b) => b.date - a.date);
}, [items]);

// useCallback for callback props (when child is memoized)
const handleSubmit = useCallback(
    (data: FormData) => {
        mutation.mutate(data);
    },
    [mutation]
);

// React.memo for pure components
const ExpensiveList = memo(function ExpensiveList({
    items,
}: {
    items: Item[];
}) {
    return (
        <ul>
            {items.map((item) => (
                <ExpensiveItem key={item.id} item={item} />
            ))}
        </ul>
    );
});
```

### Lazy Loading

```tsx
// Component lazy loading
const HeavyChart = lazy(() => import("@/components/heavy-chart"));

function Dashboard() {
    return (
        <Suspense fallback={<ChartSkeleton />}>
            <HeavyChart data={data} />
        </Suspense>
    );
}

// Route-based code splitting (Next.js)
// Each page is automatically code-split

// Dynamic import for conditional features
const AdminPanel = dynamic(() => import("@/components/admin-panel"), {
    loading: () => <AdminPanelSkeleton />,
    ssr: false,
});
```

### Virtualization

```tsx
import { useVirtualizer } from "@tanstack/react-virtual";

function VirtualList({ items }: { items: Item[] }) {
    const parentRef = useRef<HTMLDivElement>(null);

    const virtualizer = useVirtualizer({
        count: items.length,
        getScrollElement: () => parentRef.current,
        estimateSize: () => 50,
        overscan: 5,
    });

    return (
        <div ref={parentRef} className="h-96 overflow-auto">
            <div
                style={{
                    height: `${virtualizer.getTotalSize()}px`,
                    position: "relative",
                }}
            >
                {virtualizer.getVirtualItems().map((virtualRow) => (
                    <div
                        key={virtualRow.key}
                        style={{
                            position: "absolute",
                            top: 0,
                            left: 0,
                            width: "100%",
                            height: `${virtualRow.size}px`,
                            transform: `translateY(${virtualRow.start}px)`,
                        }}
                    >
                        <ListItem item={items[virtualRow.index]} />
                    </div>
                ))}
            </div>
        </div>
    );
}
```

### Optimistic Updates

```tsx
const queryClient = useQueryClient();

const mutation = useMutation({
    mutationFn: updateTodo,
    onMutate: async (newTodo) => {
        // Cancel outgoing refetches
        await queryClient.cancelQueries({ queryKey: ["todos"] });

        // Snapshot previous value
        const previousTodos = queryClient.getQueryData(["todos"]);

        // Optimistically update
        queryClient.setQueryData(["todos"], (old: Todo[]) =>
            old.map((todo) => (todo.id === newTodo.id ? newTodo : todo))
        );

        return { previousTodos };
    },
    onError: (err, newTodo, context) => {
        // Rollback on error
        queryClient.setQueryData(["todos"], context?.previousTodos);
    },
    onSettled: () => {
        // Refetch after mutation
        queryClient.invalidateQueries({ queryKey: ["todos"] });
    },
});
```

## TypeScript Patterns

### Component Props

```tsx
// Extend HTML element props
interface ButtonProps extends React.ComponentPropsWithoutRef<"button"> {
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

// With ref forwarding
interface InputProps extends React.ComponentPropsWithRef<"input"> {
  label?: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className, ...props }, ref) => {
    return (/* ... */);
  }
);
```

### Discriminated Unions

```tsx
// For components with mutually exclusive props
type ButtonProps =
    | { href: string; onClick?: never } // Link button
    | { href?: never; onClick: () => void }; // Click button

function Button(props: ButtonProps & { children: React.ReactNode }) {
    if (props.href) {
        return <a href={props.href}>{props.children}</a>;
    }
    return <button onClick={props.onClick}>{props.children}</button>;
}
```

### Generic Components

```tsx
interface SelectProps<T> {
    options: T[];
    value: T | null;
    onChange: (value: T) => void;
    getLabel: (option: T) => string;
    getValue: (option: T) => string;
}

function Select<T>({
    options,
    value,
    onChange,
    getLabel,
    getValue,
}: SelectProps<T>) {
    return (
        <select
            value={value ? getValue(value) : ""}
            onChange={(e) => {
                const selected = options.find(
                    (opt) => getValue(opt) === e.target.value
                );
                if (selected) onChange(selected);
            }}
        >
            <option value="">Select...</option>
            {options.map((option) => (
                <option key={getValue(option)} value={getValue(option)}>
                    {getLabel(option)}
                </option>
            ))}
        </select>
    );
}

// Usage
<Select
    options={users}
    value={selectedUser}
    onChange={setSelectedUser}
    getLabel={(user) => user.name}
    getValue={(user) => user.id}
/>;
```

### Polymorphic Components

```tsx
type PolymorphicProps<E extends React.ElementType> = {
  as?: E;
  children: React.ReactNode;
} & Omit<React.ComponentPropsWithoutRef<E>, "as" | "children">;

function Text<E extends React.ElementType = "span">({
  as,
  children,
  ...props
}: PolymorphicProps<E>) {
  const Component = as || "span";
  return <Component {...props}>{children}</Component>;
}

// Usage
<Text>Span by default</Text>
<Text as="p">Paragraph</Text>
<Text as="h1">Heading</Text>
<Text as="label" htmlFor="input">Label</Text>
```

## Anti-Patterns

### ❌ Prop Drilling

```tsx
// Bad
<App>
  <Layout user={user}>
    <Sidebar user={user}>
      <UserMenu user={user} />
    </Sidebar>
  </Layout>
</App>

// Good - use context
<UserProvider value={user}>
  <App>
    <Layout>
      <Sidebar>
        <UserMenu /> {/* Gets user from context */}
      </Sidebar>
    </Layout>
  </App>
</UserProvider>
```

### ❌ Premature Optimization

```tsx
// Bad - unnecessary memoization
const SimpleComponent = memo(({ title }: { title: string }) => (
    <h1>{title}</h1>
));

// Good - memoize only when necessary
// (expensive renders, frequent parent re-renders, reference-stable callbacks)
```

### ❌ useEffect for Derived State

```tsx
// Bad
const [items, setItems] = useState<Item[]>([]);
const [filteredItems, setFilteredItems] = useState<Item[]>([]);

useEffect(() => {
    setFilteredItems(items.filter((item) => item.active));
}, [items]);

// Good - derive during render
const [items, setItems] = useState<Item[]>([]);
const filteredItems = useMemo(
    () => items.filter((item) => item.active),
    [items]
);
```

### ❌ Index as Key (When Order Changes)

```tsx
// Bad - keys change when order changes
{
    items.map((item, index) => <ListItem key={index} item={item} />);
}

// Good - stable unique key
{
    items.map((item) => <ListItem key={item.id} item={item} />);
}
```

### ❌ Object/Array Literals in Props

```tsx
// Bad - creates new reference every render
<Component style={{ color: "red" }} />
<Component items={[1, 2, 3]} />

// Good - stable references
const style = { color: "red" };
const items = [1, 2, 3];

<Component style={style} />
<Component items={items} />

// Or define outside component if static
const ITEMS = [1, 2, 3];
```

### ❌ Async in useEffect Without Cleanup

```tsx
// Bad - potential memory leak
useEffect(() => {
    fetchData().then(setData);
}, []);

// Good - with cleanup
useEffect(() => {
    let cancelled = false;

    fetchData().then((data) => {
        if (!cancelled) setData(data);
    });

    return () => {
        cancelled = true;
    };
}, []);

// Better - use React Query or SWR
const { data } = useQuery({ queryKey: ["data"], queryFn: fetchData });
```
