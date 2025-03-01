import uvicorn
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager


from app.notes.router import note_router
from app.authentication.router import auth_router
from app.scheduler import start_scheduler
from app.users.router import users_router
from fastapi.security import HTTPBearer

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

http_bearer = HTTPBearer(auto_error=False)


app.include_router(
    note_router,
    dependencies=[Depends(http_bearer)],

)
app.include_router(auth_router)
app.include_router(users_router)



@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    yield
    scheduler.shutdown()


app.router.lifespan_context = lifespan


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
