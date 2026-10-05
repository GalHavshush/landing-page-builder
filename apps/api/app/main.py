from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.assets.routes import router as assets_router
from app.auth.routes import router as auth_router
from app.config import get_settings
from app.members.routes import router as members_router
from app.posts.routes import router as posts_router
from app.projects.output import router as output_router
from app.projects.routes import router as projects_router

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def create_app() -> FastAPI:
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

    app.include_router(auth_router)
    app.include_router(projects_router)
    app.include_router(output_router)
    app.include_router(assets_router)
    app.include_router(posts_router)
    app.include_router(members_router)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
