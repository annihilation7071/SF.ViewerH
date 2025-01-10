from backend import dep
from fastapi import APIRouter, Request, HTTPException, Body
from backend.projects.cls import Projects, Project
from backend import utils, downloader
from sqlalchemy import func, select
from backend.logger_new import get_logger

log = get_logger("Routers.extra")

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

    with dep.Session() as session:
        flt = (
            Project.source == site,
            Project.source_id == int(id_),
        )

        stmt = select(func.count(Project.lid)).where(*flt)

        find_projects = session.scalar(stmt)

    log.debug(f"find_projects_count={find_projects}")

    if find_projects > 0:
        return {"status": "found"}
    else:
        return {"status": "not found"}