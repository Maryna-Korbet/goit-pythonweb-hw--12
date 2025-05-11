from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from slowapi.errors import RateLimitExceeded

from src.routes import contacts_route, auth_route
from src.database.db import get_db, sessionmanager
from src.config import messages


schedulers = AsyncIOScheduler()


async def cleanup_expired_tokens():
    """Cleanup expired tokens."""
    async with sessionmanager.session() as db:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=7)
        stmt = text(
            "DELETE FROM refresh_tokens WHERE expired_at < :now OR (revoked_at IS NOT NULL AND expired_at < :cutoff)"
        )
        await db.execute(stmt, {"now": now, "cutoff": cutoff})
        await db.commit()
        print(f"Expired tokens cleaned up at [{now.strftime('%Y-%m-%d %H:%M:%S')}]")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """App lifespan."""
    schedulers.add_job(cleanup_expired_tokens, "interval", hours=1)
    schedulers.start()
    yield
    schedulers.shutdown()


app = FastAPI(
    lifespan=lifespan,
    title="Contacts App",
    description="App for storing and managing contacts",
    version="1.0",
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Rate limit handler."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": messages.requests_limit.get("en")},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(contacts_route.router, prefix="/api")
app.include_router(auth_route.router, prefix="/api")


@app.get("/")
def read_root(request: Request):
    """Root endpoint."""
    return {"message": "Contacts_app v1.0"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """Healthchecker endpoint."""
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database is not configured correctly",
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database",
        )