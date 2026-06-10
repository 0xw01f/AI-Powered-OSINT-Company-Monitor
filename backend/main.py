"""FastAPI entry point for the OSINT monitor backend."""

from fastapi import FastAPI

app = FastAPI(title='AI-Powered OSINT Company Monitor')


@app.get('/')
def read_root() -> dict[str, str]:
    """Health check endpoint."""
    return {'message': 'OSINT Monitor API is running'}
