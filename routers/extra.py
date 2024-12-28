from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from backend.projects.cls import Projects, Project
from backend import utils, downloader
from icecream import ic
ic.configureOutput(includeContext=True)

# noinspection PyTypeChecker
projects: Projects = None

router = APIRouter()


@router.post("/load")
async def load(data: dict):
    downloader.download(data.get("url"))
    return JSONResponse({"status": "success"})


@router.post("/get-status")
async def get_status(request: Request):
    data = await request.json()
    url = data.get("url")
    ic(url)

    if not url:
        raise HTTPException(status_code=400, detail="URL not received")

    if url == "test":
        return {"statur": "test"}

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