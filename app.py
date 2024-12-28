from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.projects.cls import Projects
from backend.projects.putils import update_projects
from fastapi.middleware.cors import CORSMiddleware
from routers import main, extra


projects = Projects()
main.projects = projects
extra.projects = projects
update_projects(projects)
projects.checking()

app = FastAPI()
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