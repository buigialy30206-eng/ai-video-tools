from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class CacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        path = request.url.path
        if path.startswith("/static/"):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response


class RedirectMiddleware(BaseHTTPMiddleware):
    """301 redirect from the old fly.dev domain to the custom domain."""

    async def dispatch(self, request: Request, call_next):
        host = request.headers.get("host", "").split(":")[0]
        if host in ("ai-video-tools.fly.dev", "www.aivideotest.com"):
            target = f"https://aivideotest.com{request.url.path}"
            if request.url.query:
                target += f"?{request.url.query}"
            return RedirectResponse(target, status_code=301)
        return await call_next(request)


app = FastAPI(title="AI Video Tools")
app.add_middleware(CacheMiddleware)
app.add_middleware(SecurityMiddleware)
app.add_middleware(RedirectMiddleware)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def read_static(filename: str, content_type: str) -> Response:
    path = os.path.join(STATIC_DIR, filename)
    if not os.path.exists(path):
        return Response("Not Found", status_code=404)
    with open(path, "r", encoding="utf-8") as f:
        return Response(content=f.read(), media_type=content_type)


def serve_template(filename: str) -> HTMLResponse:
    path = os.path.join(TEMPLATES_DIR, filename)
    if not os.path.exists(path):
        return HTMLResponse("<h1>Page not found</h1>", status_code=404)
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/robots.txt")
async def robots():
    return read_static("robots.txt", "text/plain")


@app.get("/sitemap.xml")
async def sitemap():
    return read_static("sitemap.xml", "application/xml")


@app.get("/google19449868d7d18dbd.html")
async def google_verify():
    return read_static("google19449868d7d18dbd.html", "text/html")


@app.get("/", response_class=HTMLResponse)
async def home():
    return serve_template("index.html")


@app.get("/synthesia-vs-heygen-vs-runway", response_class=HTMLResponse)
async def compare():
    return serve_template("synthesia-vs-heygen-vs-runway.html")


@app.get("/no-camera", response_class=HTMLResponse)
async def no_camera():
    return serve_template("no-camera.html")


@app.get("/ai-avatars", response_class=HTMLResponse)
async def ai_avatars():
    return serve_template("ai-avatars.html")


@app.get("/pricing", response_class=HTMLResponse)
async def pricing():
    return serve_template("pricing.html")


@app.get("/short-form", response_class=HTMLResponse)
async def short_form():
    return serve_template("short-form.html")


@app.get("/clone-yourself", response_class=HTMLResponse)
async def clone_yourself():
    return serve_template("clone-yourself.html")


@app.api_route("/health", methods=["GET", "HEAD", "OPTIONS", "POST"])
async def health():
    return {"status": "ok", "pages": 7, "domain": "aivideotest.com"}
