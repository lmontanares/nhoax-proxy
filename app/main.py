from contextlib import asynccontextmanager
from sqlite3 import OperationalError

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import get_db_path, init_db, is_url_malicious


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="NHoax Proxy", lifespan=lifespan)


@app.exception_handler(OperationalError)
async def db_error_handler(request: Request, exc: OperationalError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"detail": "Service unavailable"})


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, (HTTPException, RequestValidationError)):
        raise exc
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/urlinfo/1/{hostname_and_port}/{path:path}")
def lookup(hostname_and_port: str, path: str, db_path: str = Depends(get_db_path)) -> dict:
    url = f"{hostname_and_port}/{path}"
    return {"safe": not is_url_malicious(url, db_path)}
