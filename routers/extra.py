from backend.main_import import *
from backend import logger

log = logger.get_logger("App.routers.extra")

# noinspection PyTypeChecker
projects: Projects = None

router = APIRouter()


@router.post("/load")
async def load(request: Request,
               url: str = Body(..., embed=True)):
    await downloader.download(url, projects)
    # return JSONResponse({"status": "success"})


@router.post("/get-status")
async def get_status(
        request: Request,
        url: str = Body(..., embed=True),
):
    # data = await request.json()
    log.debug(f"url={url}")

    if not url:
        raise HTTPException(status_code=400, detail="URL not received")

    if url == "test":
        return {"status": "test"}

    url, site, id_ = utils.separate_url(url)
    log.debug(f"url={url}, site={site}, id_={id_}")

    found_projects_count = projects.check_project(site, id_)

    log.debug(f"find_projects_count={found_projects_count}")

    if found_projects_count > 0:
        return {"status": "found"}
    else:
        return {"status": "not found"}