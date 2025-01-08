from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.projects.cls import Projects
from backend.projects.updater import update_projects
from fastapi.middleware.cors import CORSMiddleware
from routers import main, extra
import os
import asyncio
from backend.logger_new import get_logger

log = get_logger("App")

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# noinspection PyTypeChecker
project: Projects = None


# noinspection PyShadowingNames
@asynccontextmanager
async def lifespan(app: FastAPI):
    # noinspection PyGlobalUndefined
    global projects
    projects = Projects()
    main.projects = projects
    extra.projects = projects
    update_projects(projects)
    projects.checking()
    yield

app = FastAPI(lifespan=lifespan)
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(main.router)
app.include_router(extra.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=1707, log_level="debug")