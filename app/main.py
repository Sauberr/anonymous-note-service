import uvicorn
from fastapi import Depends, FastAPI
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles

from app.authentication.messages import router as message_router
from app.authentication.router import router as auth_router
from app.core.config import settings
from app.notes.router import router as note_router
from app.users.router import router as user_router
from app.webhooks.user import router as webhook_router
from app.core.lifespan import lifespan

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

http_bearer = HTTPBearer(auto_error=True)


app.include_router(
    note_router,
)
app.include_router(
    user_router,
    dependencies=[Depends(http_bearer)],
)
app.include_router(auth_router)
app.include_router(message_router)

app.include_router(webhook_router)


app.router.lifespan_context = lifespan


if __name__ == "__main__":
    print(settings.api.v1.auth)
    uvicorn.run(
        app,
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
