from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.config import settings
from app.core.logging import configure_logging
from app.routers import auth, users, plans, tasks, admin, web

configure_logging()

limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.rate_limit_per_minute}/minute"])

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(web.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(plans.router)
app.include_router(tasks.router)
app.include_router(admin.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Service"] = settings.app_name
    return response


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error", "error": str(exc)})


Instrumentator().instrument(app).expose(app, include_in_schema=False, endpoint="/metrics")
