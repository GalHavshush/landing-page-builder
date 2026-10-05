import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.assets.routes import router as assets_router
from app.auth.routes import router as auth_router
from app.config import get_settings
from app.exports.routes import router as exports_router
from app.members.routes import router as members_router
from app.posts.routes import router as posts_router
from app.projects.output import router as output_router
from app.projects.routes import router as projects_router
from app.stock.routes import router as stock_router

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
log = logging.getLogger("builder")


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    app = FastAPI(title="Website Builder API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().cors_origins,
        allow_credentials=True,  # the SPA authenticates with a cookie
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def require_csrf_header(request: Request, call_next):
        """CSRF defence in depth (on top of SameSite=Lax cookies): state-changing requests must
        carry a custom header. Browsers only let same-origin JS (or CORS-approved origins) add
        one, so a form or <img> on another site cannot forge such a request."""
        if (
            request.method not in SAFE_METHODS
            and request.headers.get("x-requested-with") != "builder"
        ):
            return JSONResponse({"detail": "Missing X-Requested-With header"}, status_code=403)
        return await call_next(request)

    @app.middleware("http")
    async def observe_and_harden(request: Request, call_next):
        """Request id + access log + a safe 500 + baseline security headers on every response."""
        request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            # never leak internals to the client; the id lets you find the stack trace in the log
            log.exception(
                "unhandled error request_id=%s %s %s", request_id, request.method, request.url.path
            )
            response = JSONResponse(
                {"detail": "Something went wrong on our side.", "request_id": request_id},
                status_code=500,
            )
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["X-Frame-Options"] = "DENY"
        log.info(
            "%s %s -> %s %.0fms request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            (time.perf_counter() - started) * 1000,
            request_id,
        )
        return response

    app.include_router(auth_router)
    app.include_router(projects_router)
    app.include_router(output_router)
    app.include_router(assets_router)
    app.include_router(stock_router)
    app.include_router(posts_router)
    app.include_router(members_router)
    app.include_router(exports_router)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
