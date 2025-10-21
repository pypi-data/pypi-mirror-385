# Python, Django and async

Simple rules:

- Send long running computation to separate thread or a queue using sync_to_async
- ORM queries need to be run in a separate thread using sync_to_async` (django orm is not async ready yet)
- Middlewares need to be async compatible
- Avoir thread local or global variables, use `ContextVar` instead

## WSGI, ASGI, Thread, Workers & async loop

### WSGI and multiple workers

Python and Django originaly uses a worker model. One http request per worker. Long running computing blocks that worker for a long time. The usual way of running python is running a lot of workers on the same machine listening on the same port using a process manager like
gunicorn.

If there are less workers available than parallel incoming requests the requests are gonna wait. If it exceed a certain wait time they are gonna timeout.


```
┌───────────────────┐                                              ┌───────────────────┐
│                   │                                              │                   │
│     Request 1     │─────┐                                 ┌─────▶│  Python Worker 1  │
│                   │     │                                 │      │                   │
└───────────────────┘     │                                 │      └───────────────────┘
                          │                                 │                           
┌───────────────────┐     │                                 │      ┌───────────────────┐
│                   │     │                                 │      │                   │
│     Request 2     │─────┤                                 ├─────▶│  Python Worker 2  │
│                   │     │      ┌───────────────────┐      │      │                   │
└───────────────────┘     │      │                   │      │      └───────────────────┘
                          ├─────▶│  WSGI Supervisor  │──────┤                           
┌───────────────────┐     │      │                   │      │      ┌───────────────────┐
│                   │     │      └───────────────────┘      │      │                   │
│    Request ...    │─────┤                                 ├─────▶│ Python Worker ... │
│                   │     │                                 │      │                   │
└───────────────────┘     │                                 │      └───────────────────┘
                          │                                 │                           
┌───────────────────┐     │                                 │      ┌───────────────────┐
│                   │     │                                 │      │                   │
│     Request n     │─────┘                                 └─────▶│  Python Worker n  │
│                   │                                              │                   │
└───────────────────┘                                              └───────────────────┘
```

### ASGI and single async loop

Python recently introduced async & asgi. This allows multiple request to be processed concurently (not in parallel) in the same worker. A single worker can accept multiple request
and when an asynchronous operation happens it switches to process another request while
waiting for the result of the other request associated asynchronous operation.

```
┌───────────────────┐                                 
│                   │                                 
│     Request 1     │─────┐                           
│                   │     │                           
└───────────────────┘     │                           
                          │                           
┌───────────────────┐     │                           
│                   │     │                           
│     Request 2     │─────┤                           
│                   │     │      ┌───────────────────┐
└───────────────────┘     │      │                   │
                          ├─────▶│ASGI Python Worker │
┌───────────────────┐     │      │                   │
│                   │     │      └───────────────────┘
│    Request ...    │─────┤                           
│                   │     │                           
└───────────────────┘     │                           
                          │                           
┌───────────────────┐     │                           
│                   │     │                           
│     Request n     │─────┘                           
│                   │                                 
└───────────────────┘                                 
```

# Long running computing (or I/O)

All long running computing (more than a couple hundred ms) need to be sent to a different thread/queue/process as to not block the main async loop. Blocking the main async loop will 
result in concurent requests not being process

```python
long_running_compute_result = await sync_to_async(long_running_compute)()
```

## Async adapter functions - sync_to_async & async_to_sync

### Running sync code in the async loop: `sync_to_async`

```py
from asgiref.sync import sync_to_async


def get_data_sync():
  return requests.get("http://example.com")

get_data_async = sync_to_async(synchronous_request)


# Calling the sync function
get_data_sync()
# Calling the async function
await get_data_async()

```

### Running async code in a sync thread: `async_to_sync`


```py
from asgiref.sync import async_to_sync

async def get_data_async(...):
    ...

sync_get_data = async_to_sync(get_data_async)

result = sync_get_data()
```

The async function is run in the event loop for the current thread, if one is present. If there is no current event loop, a new event loop is spun up specifically for the single async invocation and shut down again once it completes. In either situation, the async function will execute on a different thread to the calling code.

Threadlocals and contextvars values are preserved across the boundary in both directions.

`async_to_sync()` is essentially a more powerful version of the `asyncio.run()` function in Python’s standard library. As well as ensuring threadlocals work, it also enables the `thread_sensitive` mode of `sync_to_async()` when that wrapper is used below it.

## Django ORM queries

If you want to call a part of Django that is still synchronous, like the ORM, you will need to wrap it in a `sync_to_async()` call. For example:

```py
from asgiref.sync import sync_to_async

results = await sync_to_async(Blog.objects.get, thread_sensitive=True)(pk=123)
```

You may find it easier to move any ORM code into its own function and call that entire function using sync_to_async(). For example:

```py
from asgiref.sync import sync_to_async

def _get_blog(pk):
    return Blog.objects.select_related('author').get(pk=pk)

get_blog_async = sync_to_async(_get_blog, thread_sensitive=True)

# Example call:
await get_blog_async()
```

Using the parameter `thread_sensitive=True` is important with ORM calls otherwise you are gonna get errors looking like this

```
django.db.utils.DatabaseError: DatabaseWrapper objects created in a thread
can only be used in that same thread. The object with alias 'default' was
created in thread id 4371465600 and this is thread id 6131478528.
```

- `thread_sensitive=True (the default)`: the sync function will run in the same thread as all other thread_sensitive functions. This will be the main thread, if the main thread is synchronous and you are using the async_to_sync() wrapper.
- `thread_sensitive=False`: the sync function will run in a brand new thread which is then closed once the invocation completes.


More info here: https://docs.djangoproject.com/en/4.0/topics/async/#sync-to-async

## Globals, thread locals & context var

Since a single thread is used to run multiple concurent requests storing data in a threads is highly advised against. With the upcoming async model of single threading python introduced the `ContextVar` to remediate the situation.

1. Declare a var
2. use it in one context
3. when the async loop changes request it also swaps the context

```python
var = ContextVar('var')
var.set('spam')

def main():
    # 'var' was set to 'spam' before
    # calling 'copy_context()' and 'ctx.run(main)', so:
    # var.get() == ctx[var] == 'spam'

    var.set('ham')

    # Now, after setting 'var' to 'ham':
    # var.get() == ctx[var] == 'ham'

ctx = copy_context()

# Any changes that the 'main' function makes to 'var'
# will be contained in 'ctx'.
ctx.run(main)

# The 'main()' function was run in the 'ctx' context,
# so changes to 'var' are contained in it:
# ctx[var] == 'ham'

# However, outside of 'ctx', 'var' is still set to 'spam':
# var.get() == 'spam'
```

Example use of context var: [/backend/django_context_crum/__init__.py](/backend/django_context_crum/__init__.py)
