from fastapi import APIRouter, Request, Form, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from backend.projects.cls import Projects, Project
from backend import utils, downloader
from pydantic import BaseModel
from icecream import ic
ic.configureOutput(includeContext=True)

# noinspection PyTypeChecker
projects: Projects = None

router = APIRouter()


@router.post("/load")
async def load(request: Request,
               url: str = Body(..., embed=True)):
    await downloader.download(url)
    # return JSONResponse({"status": "success"})


@router.post("/get-status")
async def get_status(
        request: Request,
        url: str = Body(..., embed=True),
):
    # data = await request.json()
    ic(url)

    if not url:
        raise HTTPException(status_code=400, detail="URL not received")

    if url == "test":
        return {"status": "test"}

    url, site, id_ = utils.separate_url(url)
    ic(url, site, id_)

    find_projects = projects.session.query(Project).filter(
        Project.source == site,
        Project.source_id == int(id_)
    ).count()

    ic(find_projects)

    if find_projects > 0:
        ic(url)
        return {"status": "found"}
    else:
        return {"status": "not found"}