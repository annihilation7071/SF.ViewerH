from backend.main_import import *
from routers import main, extra
from backend import init
from backend.db import project as project_

log = logger.get_logger("App.app")

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# noinspection PyTypeChecker
project: Projects = None


# noinspection PyShadowingNames
@asynccontextmanager
async def lifespan(app: FastAPI):
    init.init()

    # noinspection PyGlobalUndefined
    global projects
    dep.libs = Libs.load()
    dep.Session = connect.get_session()
    projects = Projects()
    dep.projects = projects
    main.projects = projects
    extra.projects = projects
    if config.app.renew_projects_when_startup:
        projects.update_projects()
        projects.backup_variants()
        projects.renew()
    log.debug(id(dep))
    log.debug(dep.Session)
    log.debug(dep.libs)
    yield
    if config.app.backup_variants_when_shutdown:
        projects.backup_variants()

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

app.mount("/static", StaticFiles(directory="static", check_dir=True), name="static")

app.include_router(main.router)
app.include_router(extra.router)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.server.ip,
        port=config.server.port,
        log_level=config.logger.fastapi_log_level if config.logger.fastapi_log else None
    )