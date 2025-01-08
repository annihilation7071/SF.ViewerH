from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from backend.projects.cls import Projects
from backend.utils import get_visible_pages
from pathlib import Path
# noinspection PyUnresolvedReferences
from urllib.parse import quote, unquote
import mimetypes
from backend.editor import selector as edit_selector
from backend.logger_new import get_logger

log = get_logger("Routers.main")

# noinspection PyTypeChecker
projects: Projects = None
project_cache: dict = {}

PROJECTS_PER_PAGE = 60
PPG = PROJECTS_PER_PAGE
templates = Jinja2Templates(directory="templates")

router = APIRouter()


def clear_cache():
    global project_cache
    project_cache = {}


def get_with_cache(project_lid: str):
    global project_cache

    if project_lid not in project_cache:
        project = projects.get_project_by_lid(project_lid)
        images = project.get_images()
        project_cache = {
            project_lid: {
                "data": project,
                "images": images
            }
        }
    else:
        project = project_cache[project_lid]["data"]
        if "images" not in project_cache[project_lid]:
            images = project.get_images()
            project_cache[project_lid]["images"] = images
        else:
            images = project_cache[project_lid]["images"]

    return project, images


@router.get("/", response_class=HTMLResponse, name="index")
async def index(request: Request, page: int = 1, search: str = ""):
    log.debug(f"index")
    search_query = search.strip().lower()
    displayed_projects = projects.get_page(PPG, page=page, search=search_query)

    total_pages = (projects.len() + PPG - 1) // PPG
    visible_pages = get_visible_pages(page, total_pages)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "projects": displayed_projects,
            "current_page": page,
            "total_pages": total_pages,
            "visible_pages": visible_pages,
        },
    )


# @router.get("/project/{project_id}", response_class=HTMLResponse)
# async def detail_view(request: Request, project_id: int):
#     project = projects.get_project_by_id(project_id)
#     images = utils.get_pages(project)
#     return templates.TemplateResponse(
#         "detailview.html",
#         {
#             "request": request,
#             "project": project,
#             "images": images
#         },
#     )


@router.get("/project/lid/{project_lid}", response_class=HTMLResponse)
async def detail_view(request: Request, project_lid: str):
    project, images = get_with_cache(project_lid)

    return templates.TemplateResponse(
        "detailview.html",
        {
            "request": request,
            "project": project,
            "images": images
        },
    )


# @router.get("/project/{project_id}/{page_id}", response_class=HTMLResponse)
# async def reader(request: Request, project_id: int, page_id: int):
#     project = projects.get_project_by_id(project_id)
#     images = utils.get_pages(project)
#     page = page_id
#     image = images[page - 1]["path"]
#     total_pages = len(images)
#     visible_pages = get_visible_pages(page, total_pages)
#     return templates.TemplateResponse(
#         "reader.html",
#         {
#             "request": request,
#             "image": image,
#             "current_page": page,
#             "project_id": project_id,
#             "total_pages": total_pages,
#             "visible_pages": visible_pages,
#         },
#     )


@router.get("/project/lid/{project_lid}/{page_id}", response_class=HTMLResponse)
async def reader(request: Request, project_lid: str, page_id: int):
    project, images = get_with_cache(project_lid)

    page = page_id
    image = images[page - 1]["path"]
    total_pages = len(images)
    visible_pages = get_visible_pages(page, total_pages)
    return templates.TemplateResponse(
        "reader.html",
        {
            "request": request,
            "image": image,
            "current_page": page,
            "project_lid": project_lid,
            "total_pages": total_pages,
            "visible_pages": visible_pages,
        },
    )


@router.get("/get_image/{image_path:path}")
async def get_image(image_path: str | Path):
    try:
        decoded_path = unquote(image_path)
        mimetype, _ = mimetypes.guess_type(image_path)
        return FileResponse(image_path, media_type=mimetype)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Image not found")


@router.get("/items/{item}", response_class=HTMLResponse)
async def items_list(request: Request, item: str):
    support = ["tag", "character", "series",
               "parody", "artist"]

    if item in support:
        items_count = projects.count_item(item)
    else:
        raise Exception(f"{item} is not supported")

    return templates.TemplateResponse(
        "items.html",
        {
            "request": request,
            "items": items_count,
            "find": item
        }
    )


@router.post("/edit_data")
async def edit_data(
    request: Request,
    edit_type: str = Form(..., alias="edit-type"),
    data: str = Form(..., alias="edit-data"),
    url: str = Form(...),
    lid: str = Form(...),
    page: int = Form(...),
    search: str = Form(...),
):
    clear_cache()

    project = projects.get_project_by_lid(lid)

    r = edit_selector.edit(projects, project, edit_type, data)
    if r:
        return RedirectResponse(
            f"/project/lid/{r}?page={page}&search={search}", status_code=303
        )
    else:
        if lid.startswith("pool_") is False:
            return RedirectResponse(
                f"/project/lid/{lid}?page={page}&search={search}", status_code=303
            )
        else:
            return RedirectResponse(
                f"/?page={page}&search={search}", status_code=303
            )


@router.post("/sorting")
async def sorting(
    request: Request,
    sorting_method: str = Form(..., alias="sorting-method"),
    search: str = Form(...)
):

    projects.select_sorting_method(sorting_method)

    return RedirectResponse(
        f"/?page=1&search={search}", status_code=303
    )


@router.post("/pages_count")
async def pages_count(
    request: Request,
    pages_cnt: str = Form(..., alias="pages-count"),
    search: str = Form(...)
):

    global PPG
    PPG = int(pages_cnt)

    return RedirectResponse(
        f"/?page=1&search={search}", status_code=303
    )
