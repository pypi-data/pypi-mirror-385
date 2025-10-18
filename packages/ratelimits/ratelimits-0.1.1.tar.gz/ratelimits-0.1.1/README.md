# ratelimiter

A small Python library that provides simple function decorators for rate limiting using either a fixed-window (bursty) or a sliding-window (steady) strategy.


Example — Fixed window (bursty)
```
from ratelimiter import ratelimiter

@ratelimiter("fixed_window", calls=10, period=60)
def my_task(x):
    print("task", x)
```

Example — Sliding window (steady, evenly spaced)
```
from ratelimiter import ratelimiter

@ratelimiter("sliding_window", calls=30, period=60, debug=True)
def api_call(payload):
    return payload
```

### Parameters Summary

| Parameter | Type | Description |
|------------|------|-------------|
| **calls** | `int` | Maximum number of calls allowed per window. |
| **period** | `int` \| `float` | Duration of the window in seconds. |
| **offset_start** / **offset_end** | *(FixedWindow only)* | Optional adjustments for the start and end edges of the window. |
| **debug** | `bool` | Enables verbose logging to stdout for debugging and tracing sleep intervals. |
