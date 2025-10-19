"""
FynX Store - Reactive State Management Components
=================================================

This module provides the core components for reactive state management in FynX,
enabling you to create organized, reactive state containers that group related
observables together with convenient subscription and state management methods.

Why Use Stores?
---------------

Stores help you organize your application's reactive state into logical units. Instead
of having observables scattered throughout your codebase, Stores group related data
together and provide convenient methods for subscribing to changes, serializing state,
and managing the reactive lifecycle.

Stores are particularly useful for:
- **Application State**: Global app state like user preferences, theme settings
- **Feature State**: State for specific features like shopping cart, user profile
- **Component State**: Local state that needs to be shared across multiple components
- **Business Logic**: Computed values and derived state based on raw data

Core Components
---------------

**Store**: A base class for creating reactive state containers. Store classes can define
observable attributes using the `observable()` descriptor, and automatically provide
methods for subscribing to changes and managing state.

**observable**: A descriptor function that creates observable attributes on Store classes.
Use this to define reactive properties in your Store subclasses.

**StoreSnapshot**: An immutable snapshot of store state at a specific point in time,
useful for debugging, logging, and ensuring consistent state access.

**StoreMeta**: A metaclass that automatically converts observable attributes to descriptors
and provides type hint compatibility for mypy.

Key Features
------------

- **Automatic Observable Management**: Store metaclass handles observable creation
- **Convenient Subscriptions**: Subscribe to all changes or individual observables
- **State Serialization**: Save and restore store state with `to_dict()` and `load_state()`
- **Type Safety**: Full type hint support for better IDE experience
- **Memory Efficient**: Automatic cleanup and efficient change detection
- **Composable**: Easy to combine and nest multiple stores

Basic Usage
-----------

```python
from fynx import Store, observable

class CounterStore(Store):
    count = observable(0)
    name = observable("My Counter")

# Access values like regular attributes
print(CounterStore.count)  # 0
CounterStore.count = 5     # Updates the observable

# Subscribe to all changes in the store
@CounterStore.subscribe
def on_store_change(snapshot):
    print(f"Store changed: count={snapshot.count}, name={snapshot.name}")

CounterStore.count = 10  # Triggers: "Store changed: count=10, name=My Counter"
```

Advanced Patterns
-----------------

### Computed Properties in Stores

```python
from fynx import Store, observable

class UserStore(Store):
    first_name = observable("John")
    last_name = observable("Doe")
    age = observable(30)

    # Computed properties using the >> operator
    full_name = (first_name | last_name) >> (
        lambda fname, lname: f"{fname} {lname}"
    )

    is_adult = age >> (lambda a: a >= 18)

print(UserStore.full_name)  # "John Doe"
UserStore.first_name = "Jane"
print(UserStore.full_name)  # "Jane Doe" (automatically updated)
```

### State Persistence

```python
# Save store state
state = CounterStore.to_dict()
# state = {"count": 10, "name": "My Counter"}

# Restore state later
CounterStore.load_state(state)
print(CounterStore.count)  # 10
```

### Store Composition

```python
class AppStore(Store):
    theme = observable("light")
    language = observable("en")

class UserStore(Store):
    name = observable("Alice")
    preferences = observable({})

# Use both stores independently
AppStore.theme = "dark"
UserStore.name = "Bob"
```

Store Lifecycle
---------------

Stores automatically manage the lifecycle of their observables:

1. **Creation**: When you define a Store subclass, the metaclass automatically
   converts `observable()` calls into reactive descriptors.

2. **Access**: When you access store attributes, you get transparent reactive values
   that behave like regular Python attributes.

3. **Updates**: When you assign to store attributes, the underlying observables are
   updated and all dependent computations and reactions are notified.

4. **Cleanup**: Reactive contexts are automatically cleaned up when no longer needed.

Performance Considerations
--------------------------

- **Efficient Updates**: Only notifies subscribers when values actually change
- **Lazy Evaluation**: Computed properties only recalculate when accessed
- **Memory Management**: Automatic cleanup of unused reactive contexts
- **Batch Updates**: Multiple changes in quick succession are efficiently handled

Best Practices
--------------

- **Group Related State**: Keep related observables together in the same store
- **Use Descriptive Names**: Name your stores and observables clearly
- **Avoid Large Stores**: Split very large stores into smaller, focused ones
- **Use Computed for Derived State**: Don't store derived values manually
- **Handle Errors**: Reactive functions should handle exceptions gracefully
- **Document Store Purpose**: Use docstrings to explain what each store manages

Common Patterns
---------------

**Singleton Stores**: Use class-level access for global state:

```python
class GlobalStore(Store):
    is_loading = observable(False)
    current_user = observable(None)

# Access globally
GlobalStore.is_loading = True
```

**Instance Stores**: Create store instances for per-component state:

```python
class TodoStore(Store):
    items = observable([])
    filter = observable("all")

store = TodoStore()  # Instance with its own state
```

**Store Communication**: Stores can reference each other:

```python
class AuthStore(Store):
    is_logged_in = observable(False)
    user_id = observable(None)

class DataStore(Store):
    @computed
    def can_fetch_data(self):
        return AuthStore.is_logged_in
```

Migration from Plain Observables
---------------------------------

If you're using plain observables and want to migrate to Stores:

```python
# Before: Plain observables
user_name = observable("Alice")
user_age = observable(30)

# After: Store-based
class UserStore(Store):
    name = observable("Alice")
    age = observable(30)

# Access remains similar
UserStore.name = "Bob"  # Instead of user_name.set("Bob")
```

Error Handling
--------------

Stores handle errors gracefully:

- Observable updates that fail don't break the reactive system
- Computed property errors are logged but don't prevent other updates
- Store serialization handles missing or invalid data

Debugging
---------

Use StoreSnapshot for debugging:

```python
# Capture current state
snapshot = StoreSnapshot(CounterStore, CounterStore._get_observable_attrs())
print(snapshot)  # Shows all observable values

# Compare states
old_snapshot = snapshot
# ... do some operations ...
new_snapshot = StoreSnapshot(CounterStore, CounterStore._get_observable_attrs())
# Compare old_snapshot and new_snapshot
```

See Also
--------

- `fynx.observable`: Core observable classes and operators
- `fynx.computed`: Creating computed properties
- `fynx.reactive`: Reactive decorators for side effects
- `fynx.watch`: Conditional reactive functions
"""

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

from .observable import Observable, SubscriptableDescriptor
from .observable.computed import ComputedObservable

T = TypeVar("T")

# Type alias for session state values (used for serialization)
SessionValue = Union[
    None, str, int, float, bool, Dict[str, "SessionValue"], List["SessionValue"]
]


class StoreSnapshot:
    """
    Immutable snapshot of store observable values at a specific point in time.
    """

    def __init__(self, store_class: Type, observable_attrs: List[str]):
        self._store_class = store_class
        self._observable_attrs = observable_attrs
        self._snapshot_values: Dict[str, SessionValue] = {}
        self._take_snapshot()

    def _take_snapshot(self) -> None:
        """Capture current values of all observable attributes."""
        for attr_name in self._observable_attrs:
            if attr_name in self._store_class._observables:
                observable = self._store_class._observables[attr_name]
                self._snapshot_values[attr_name] = observable.value
            else:
                # For attributes that exist in the class but aren't observables,
                # get their value directly from the class
                try:
                    self._snapshot_values[attr_name] = getattr(
                        self._store_class, attr_name
                    )
                except AttributeError:
                    # If attribute doesn't exist at all, store None
                    self._snapshot_values[attr_name] = None

    def __getattr__(self, name: str) -> Any:
        """Access snapshot values or fall back to class attributes."""
        if name in self._snapshot_values:
            return self._snapshot_values[name]
        return getattr(self._store_class, name)

    def __repr__(self) -> str:
        if not self._snapshot_values:
            return "StoreSnapshot()"
        fields = [
            f"{name}={self._snapshot_values[name]!r}"
            for name in self._observable_attrs
            if name in self._snapshot_values
        ]
        return f"StoreSnapshot({', '.join(fields)})"


def observable(initial_value: Optional[T] = None) -> Any:
    """
    Create an observable with an initial value, used as a descriptor in Store classes.
    """
    return Observable("standalone", initial_value)


# Type alias for subscriptable observables (class variables)
Subscriptable = SubscriptableDescriptor[Optional[T]]


class StoreMeta(type):
    """
    Metaclass for Store to automatically convert observable attributes to descriptors
    and adjust type hints for mypy compatibility.
    """

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> Type:
        # Process annotations and replace observable instances with descriptors
        annotations = namespace.get("__annotations__", {})
        new_namespace = namespace.copy()
        observable_attrs = []

        for attr_name, attr_value in namespace.items():
            if isinstance(attr_value, Observable):
                observable_attrs.append(attr_name)
                # Wrap all observables (including computed ones) in descriptors
                initial_value = attr_value.value
                new_namespace[attr_name] = SubscriptableDescriptor(
                    initial_value=initial_value, original_observable=attr_value
                )

        new_namespace["__annotations__"] = annotations
        cls = super().__new__(mcs, name, bases, new_namespace)

        # Cache observable attributes and their instances for efficient access
        cls._observable_attrs = list(observable_attrs)
        # Store the original observables from the namespace before they get replaced
        cls._observables = {attr: namespace[attr] for attr in observable_attrs}

        return cls

    def __setattr__(cls, name: str, value: Any) -> None:
        """Intercept class attribute assignment for observables."""
        if hasattr(cls, "_observables") and name in getattr(cls, "_observables", {}):
            # It's a known observable, delegate to its set method
            getattr(cls, "_observables")[name].set(value)
        else:
            super().__setattr__(name, value)


class Store(metaclass=StoreMeta):
    """
    Base class for reactive state containers with observable attributes.

    Store provides a convenient way to group related observable values together
    and manage their lifecycle as a cohesive unit. Store subclasses can define
    observable attributes using the `observable()` descriptor, and Store provides
    methods for subscribing to changes, serializing state, and managing the
    reactive relationships.

    Key Features:
    - Automatic observable attribute detection and management
    - Convenient subscription methods for reacting to state changes
    - Serialization/deserialization support for persistence
    - Snapshot functionality for debugging and state inspection

    Example:
        ```python
        from fynx import Store, observable

        class CounterStore(Store):
            count = observable(0)
            name = observable("Counter")

        # Subscribe to all changes
        @CounterStore.subscribe
        def on_change(snapshot):
            print(f"Counter: {snapshot.count}, Name: {snapshot.name}")

        # Changes trigger reactions
        CounterStore.count = 5  # Prints: Counter: 5, Name: Counter
        CounterStore.name = "My Counter"  # Prints: Counter: 5, Name: My Counter
        ```

    Note:
        Store uses a metaclass to intercept attribute assignment, allowing
        `Store.attr = value` syntax to work seamlessly with observables.
    """

    # Class attributes set by metaclass
    _observable_attrs: List[str]
    _observables: Dict[str, Observable]

    @classmethod
    def _get_observable_attrs(cls) -> List[str]:
        """Get observable attribute names in definition order."""
        return list(cls._observable_attrs)

    @classmethod
    def _get_primitive_observable_attrs(cls) -> List[str]:
        """Get primitive (non-computed) observable attribute names for persistence."""
        return [
            attr
            for attr in cls._observable_attrs
            if not isinstance(cls._observables[attr], ComputedObservable)
        ]

    @classmethod
    def to_dict(cls) -> Dict[str, SessionValue]:
        """Serialize all observable values to a dictionary."""
        return {attr: observable.value for attr, observable in cls._observables.items()}

    @classmethod
    def load_state(cls, state_dict: Dict[str, SessionValue]) -> None:
        """Load state from a dictionary into the store's observables."""
        for attr_name, value in state_dict.items():
            if attr_name in cls._observables:
                cls._observables[attr_name].set(value)

    @classmethod
    def subscribe(cls, func: Callable[[StoreSnapshot], None]) -> None:
        """Subscribe a function to react to all observable changes in the store."""
        snapshot = StoreSnapshot(cls, cls._observable_attrs)

        def store_reaction():
            snapshot._take_snapshot()
            func(snapshot)

        context = Observable._create_subscription_context(store_reaction, func, None)
        # Subscribe to all observables (including computed ones)
        context._store_observables = list(cls._observables.values())
        for observable in context._store_observables:
            observable.add_observer(context.run)

    @classmethod
    def unsubscribe(cls, func: Callable) -> None:
        """Unsubscribe a function from all observables."""
        Observable._dispose_subscription_contexts(func)
