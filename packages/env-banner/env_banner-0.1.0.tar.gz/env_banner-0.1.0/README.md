# Environment Banner for Python (`env-banner`)

A single, portable Python utility to display an environment warning banner (e.g., "DEVELOPMENT", "STAGING") across any web framework. One source of truth, one-line usage per app.

This package provides consistent behavior across your entire technology stack. For Node.js projects, see [env-banner-node](https://github.com/sagearbor/env-banner-node).

## Why This Exists

In a complex development environment with multiple repositories and environments (dev, test, staging), it's easy to accidentally use a non-production system with production data. This utility prevents such mistakes by displaying a clear, unavoidable banner on all non-production deployments.

This library is designed to be:

* **Portable**: A single package that works in any Python web project.
* **Bulletproof**: Uses reliable server-side detection and sane defaults. It fails safe by showing a banner if the environment is unknown.
* **Thoughtless**: Requires only a one-line integration for most major frameworks.
* **Framework-Agnostic**: Works with FastAPI, Starlette, Flask, Django, Dash, and Streamlit out of the box.
* **Maintainable**: All banner logic, colors, and rules are in one place. Update it once, and all projects inherit the changes.

## Repository Structure

The repository is structured as a standard Python package.

```
env-banner-python/
├── envbanner/
│   ├── __init__.py
│   ├── adapters.py
│   ├── core.py
│   ├── middleware.py
│   └── streamlit_adapter.py
├── test/               # Test files (not published to PyPI)
│   ├── flask-app.py
│   ├── test-*.html
│   └── README.md
├── LICENSE
├── pyproject.toml
└── README.md
```

**Note:** The `test/` directory is excluded from PyPI packages via `pyproject.toml`.

## Installation

Install from PyPI (once published):

```bash
pip install env-banner
```

Or install directly from the Git repository:

```bash
pip install "git+https://github.com/sagearbor/env-banner-python.git#egg=env-banner"
```

## How It Works

The utility uses a middleware-first approach.

1.  **Environment Classification**: It determines the current environment by checking the `APP_ENV` environment variable first, then falling back to reliable server-side request details (host, path). It defaults to `dev` if uncertain.
2.  **Middleware Injection (WSGI/ASGI)**: For frameworks like Flask, FastAPI, and Django, it uses a middleware to automatically inject the banner HTML into any `text/html` response just before it's sent to the browser.
3.  **Adapters (Dash/Streamlit)**: For frameworks where middleware isn't a natural fit, it provides simple one-line adapter functions that patch the application or inject the banner using framework-specific methods.

## Configuration

The banner's behavior is controlled primarily by a single environment variable:

**`APP_ENV`** (or `ENVBANNER_ENV`)

Set this variable in your deployment environment (Docker, Kubernetes, etc.).

* `prod` or `production`: **No banner** is shown.
* `staging`, `val`, `preprod`: A **yellow/amber banner** is shown.
* `dev`, `test`, `local`: A **red banner** is shown.
* **If unset**: A **red banner** is shown by default.

## Usage

Import the library and add the single integration line to your application.

### FastAPI / Starlette (ASGI)

```python
from fastapi import FastAPI
from envbanner import ASGIBannerMiddleware

app = FastAPI()
app.add_middleware(ASGIBannerMiddleware)  # <-- Add this line
```

### Flask (WSGI)

```python
from flask import Flask
from envbanner import flask as envbanner_flask

app = Flask(__name__)
envbanner_flask(app)  # <-- Add this line
```

### Django

In your `settings.py`, add the middleware to your `MIDDLEWARE` list. It should be placed early in the list.

```python
# settings.py
MIDDLEWARE = [
    'envbanner.middleware.WSGIBannerMiddleware',  # <-- Add this line
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ...
]
```

### Dash

```python
import dash
from envbanner import dash as envbanner_dash

app = dash.Dash(__name__)
envbanner_dash(app)  # <-- Add this line
```

### Streamlit

Place this line near the top of your Streamlit script.

```python
import streamlit as st
import envbanner

envbanner.streamlit()  # <-- Add this line

st.title("My Streamlit App")
# ...
```

## Customization Options

All middleware and adapter functions accept optional configuration parameters:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `text` | `str` | Auto-detected (e.g., "DEV", "STAGING") | Custom text to display in the banner |
| `background` | `str` | Auto-detected (red for dev, amber for staging) | Custom background color (hex code) |
| `color` | `str` | Auto-detected (white for dev, dark gray for staging) | Custom text color (hex code) |
| `position` | `str` | `'bottom'` | Banner position: `'top'`, `'bottom'`, `'top-left'`, `'top-right'`, `'bottom-left'`, `'bottom-right'`, `'diagonal'` (or `'diagonal-bltr'`), `'diagonal-tlbr'` |
| `show_host` | `bool` | `True` | Whether to display the hostname and port (e.g., " • localhost:5000") |
| `opacity` | `float` | `1.0` (bars/ribbons), `0.5` (diagonal) | Banner opacity from 0.0 (transparent) to 1.0 (fully opaque) |
| `env_var_name` | `str` | `'APP_ENV'` | Primary environment variable name to check |

### Examples

#### Custom Text Without Hostname

```python
from flask import Flask
from envbanner import flask as envbanner_flask

app = Flask(__name__)
envbanner_flask(app, text="DON'T USE REAL DATA", show_host=False)
# Result: "DON'T USE REAL DATA" (no hostname/port shown)
```

#### Custom Text with Colors

```python
from fastapi import FastAPI
from envbanner import ASGIBannerMiddleware

app = FastAPI()
app.add_middleware(
    ASGIBannerMiddleware,
    text="QA Environment - Test Data Only",
    background="#9333ea",  # purple
    color="#ffffff",       # white
    position="bottom"
)
# Result: "QA Environment - Test Data Only • localhost:8000" at bottom
```

#### Corner Ribbon Positions

Corner positions display the banner as a diagonal ribbon in the specified corner:

```python
# Top-right corner ribbon (default ribbon style)
envbanner_flask(app, position='top-right', text="STAGING")

# Top-left corner ribbon
envbanner_flask(app, position='top-left')

# Bottom-right corner ribbon
envbanner_flask(app, position='bottom-right')

# Bottom-left corner ribbon
envbanner_flask(app, position='bottom-left')
```

#### Full Bar Positions

Full-width bar positions span the entire width of the page:

```python
# Bottom bar (default)
envbanner_flask(app)
# or explicitly:
envbanner_flask(app, position='bottom')

# Top bar
envbanner_flask(app, position='top')
```

#### Diagonal Banner

The diagonal position creates a thin diagonal stripe across the viewport, perfect for highly visible warnings without blocking content. The banner is click-through enabled (`pointer-events: none`).

Two diagonal directions are available:

```python
# Default diagonal: bottom-left to top-right (/)
envbanner_flask(app,
    position='diagonal',
    text="DON'T USE REAL DATA"
)
# or explicitly:
envbanner_flask(app,
    position='diagonal-bltr',  # BLTR = Bottom-Left To Right
    text="DON'T USE REAL DATA"
)

# Alternative direction: top-left to bottom-right (\)
envbanner_flask(app,
    position='diagonal-tlbr',  # TLBR = Top-Left To Bottom-Right
    text="STAGING ENVIRONMENT"
)

# Custom opacity diagonal
envbanner_flask(app,
    position='diagonal',
    opacity=0.3,  # 30% opaque (very subtle)
    text="DEVELOPMENT ENVIRONMENT"
)

# More visible diagonal
envbanner_flask(app,
    position='diagonal',
    opacity=0.7,  # 70% opaque
    background='#ef4444',
    color='#ffffff',
    text="STAGING - TEST DATA ONLY",
    show_host=False
)
```

**Diagonal Positions:**
- `'diagonal'` or `'diagonal-bltr'`: Bottom-left to top-right (/) - **default diagonal direction**
- `'diagonal-tlbr'`: Top-left to bottom-right (\)

#### Transparency for Other Positions

The `opacity` option works with all position styles:

```python
# Semi-transparent top bar
envbanner_flask(app,
    position='top',
    opacity=0.8,
    text="DEV ENVIRONMENT"
)

# Semi-transparent corner ribbon
envbanner_flask(app,
    position='top-right',
    opacity=0.6,
    text="STAGING"
)
```

## Testing

The `test/` directory contains standalone HTML files and a Flask test server for testing all banner positions. See `test/README.md` for details.

```bash
# Run Flask test server
pip install flask
python test/flask-app.py
```

Visit http://localhost:5000 to see the banner in action.

## License

MIT License - see LICENSE file for details.
