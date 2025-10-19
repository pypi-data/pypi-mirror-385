# Interfaces

A module can adopt a public interface by matching interface rules in [`tach.toml`](configuration.md#interfaces).

## How does it work?

When Tach is checking imports from a module with a [public interface](configuration.md#interfaces), it will verify that the import matches one of the `expose` patterns.
This prevents other modules from becoming coupled to implementation details, and makes future changes easier.

### Example

Given modules called 'core' and 'domain', we may have `tach.toml` contents like this:

```toml
[[modules]]
path = "domain"
depends_on = [
    "core"
]

[[modules]]
path = "core"
depends_on = []

[[interfaces]]
expose = ["get_data"]
from = ["core"]
```

Then, in `domain.py`, we may have:

```python
from core.main import DataModel  # This import fails

DataModel.objects.all()
```

This import would **fail** `tach check` with the following error:

```shell
❌ domain.py[L1]: Module 'core' has a public interface. Only imports from the public interface of this module are allowed. The import 'core.main.DataModel' (in module 'parsing') is not public.
```

In this case, there is a public interface defined in `tach.toml` which includes a service method to use instead.

```python
from core import get_data  # This import is OK

get_data()
```

`tach check` will now pass!

```bash
✅ All modules validated!
```


## Interface visibility

Interfaces can specify `visibility`, similar to [modules](configuration.md#modules).

This allows 'splitting' the interface, usually to support a detailed/sensitive interface for some consumers while maintaining a minimal interface by default.

### Example

```toml
[[modules]]
path = "api"
depends_on = []

[[interfaces]]
expose = ["read_data"]
from = ["api"]

[[interfaces]]
expose = ["write_data"]
from = ["api"]
visibility = ["admin.controller"]  # limiting visibility of this interface
```

In the configuration shown above, the `api` module exposes only `read_data` to most consumers,
while also providing `write_data` through an interface visible only to `admin.controller`.

You may attach an arbitrary number of interfaces to the same module, with varying `visibility`.


### Example: Exclusive interface

It is also possible to mark an interface with `exclusive: true`.

When an interface is `exclusive`, it will override all other matching interfaces for the module,
which is only relevant when using `visibility` as shown above.

Using the example above:

```toml
[[modules]]
path = "api"
depends_on = []

[[interfaces]]
expose = ["read_data"]
from = ["api"]

[[interfaces]]
expose = ["write_data"]
from = ["api"]
visibility = ["admin.controller"]
exclusive = true  # marking this interface as 'exclusive'
```

By marking the `write_data` interface as exclusive, we are saying that `admin.controller` should _exclusively_ use `api` through that interface (e.g. `write_data`).
