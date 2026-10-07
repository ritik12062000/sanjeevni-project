import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from app.config.settings import settings
from app.core.exceptions import AppError
from app.core.logging import get_app_logger
from app.database.connection import init_db
from app.routers import home, auth, chatbot, appointments, screening, injury, doctors, records

logger = get_app_logger(__name__)

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, max_age=settings.SESSION_HOURS * 3600)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("Database ready.")


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse({"success": False, "message": exc.message}, status_code=exc.status_code)


for module in (home, auth, chatbot, appointments, screening, injury, doctors, records):
    app.include_router(module.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
