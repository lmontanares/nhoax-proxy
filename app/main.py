from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.database import get_db_path, init_db, is_url_malicious


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="NHoax Proxy", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/urlinfo/1/{hostname_and_port}/{path:path}")
def lookup(hostname_and_port: str, path: str, db_path: str = Depends(get_db_path)) -> dict:
    url = f"{hostname_and_port}/{path}"
    return {"safe": not is_url_malicious(url, db_path)}
