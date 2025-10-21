import warnings

try:
    import psycopg
    import fastapi
    import python_multipart
    import httpx
    import uvicorn
except ModuleNotFoundError:
    warnings.warn("Missing optional dependencies to use the HTTP API. Install them with `pip install sunpeek [api]`")
