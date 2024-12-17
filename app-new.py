from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend import utils, downloader
from backend.editor import selector as edit_selector
from backend.projects import Projects
from backend import logger

PROJECTS_PER_PAGE = 60
PPG = PROJECTS_PER_PAGE

logger.start()

projects = Projects()
projects.update_projects()

app = FastAPI()

# Подключение шаблонов
templates = Jinja2Templates(directory="templates")

# Подключение статики
app.mount("/static", StaticFiles(directory="static"), name="static")


def get_visible_pages(current_page, total_pages):
    if total_pages <= 15:
        return list(range(1, total_pages + 1))

    visible_pages = []
    if current_page > 7:
        visible_pages.append(1)
        visible_pages.append('...')

    start_page = max(1, current_page - 7)
    end_page = min(total_pages, start_page + 15 - 1)

    if end_page == total_pages:
        start_page = max(1, total_pages - 15 + 1)

    visible_pages.extend(range(start_page, end_page + 1))

    if end_page < total_pages:
        visible_pages.append('...')
        visible_pages.append(total_pages)

    return visible_pages


@app.get("/", response_class=HTMLResponse, name="index")
async def index(request: Request, page: int = 1, search: str = ""):
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


@app.get("/project/{project_id}", response_class=HTMLResponse)
async def detail_view(request: Request, project_id: int):
    project = projects.get_project_by_id(project_id)
    images = utils.get_pages(project)
    return templates.TemplateResponse(
        "detailview.html",
        {"request": request, "project": project, "images": images},
    )

@app.get("/project/lid/{project_lid}", response_class=HTMLResponse)
async def detail_view_lid(request: Request, project_lid: str):
    project = projects.get_project_by_lid(project_lid)
    images = utils.get_pages(project)
    return templates.TemplateResponse(
        "detailview.html",
        {"request": request, "project": project, "images": images},
    )

@app.get("/project/{project_id}/{page_id}", response_class=HTMLResponse)
async def reader(request: Request, project_id: int, page_id: int):
    project = projects.get_project_by_id(project_id)
    images = utils.get_pages(project)
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
            "project_id": project_id,
            "total_pages": total_pages,
            "visible_pages": visible_pages,
        },
    )

@app.get("/get_image/{image_path:path}")
async def get_image(image_path: str):
    try:
        if image_path.endswith('.svg'):
            mimetype = 'image/svg+xml'
        else:
            mimetype = 'image/jpeg'

        return utils.get_file_response(image_path, mimetype)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Image not found")

@app.get("/items/tags", response_class=HTMLResponse)
async def tags_list(request: Request):
    item = "tag"
    tags = projects.count_item(item)
    return templates.TemplateResponse(
        "items.html", {"request": request, "items": tags, "find": item}
    )

@app.get("/items/artists", response_class=HTMLResponse)
async def artists_list(request: Request):
    item = "artist"
    tags = projects.count_item(item)
    return templates.TemplateResponse(
        "items.html", {"request": request, "items": tags, "find": item}
    )

@app.get("/items/characters", response_class=HTMLResponse)
async def characters_list(request: Request):
    item = "character"
    tags = projects.count_item(item)
    return templates.TemplateResponse(
        "items.html", {"request": request, "items": tags, "find": item}
    )

@app.get("/items/parodies", response_class=HTMLResponse)
async def parodies_list(request: Request):
    item = "parody"
    tags = projects.count_item(item)
    return templates.TemplateResponse(
        "items.html", {"request": request, "items": tags, "find": item}
    )

@app.post("/load")
async def load(data: dict):
    print("Received URL:", data.get("url"))
    downloader.download(data.get("url"))
    return JSONResponse({"status": "success"})

@app.post("/edit_data")
async def update_tags(
    request: Request,
    edit_type: str = Form(...),
    edit_data: str = Form(...),
    url: str = Form(...),
    lid: str = Form(...),
    id: int = Form(...),
    page: int = Form(...),
    search: str = Form(...),
    lvariants: str = Form(...),
):
    project = projects.get_project_by_id(int(id))
    print(project, edit_type, edit_data, url, lid, id)

    r = edit_selector.edit(
        projects, edit_type, edit_data, project, extra={"lvariants": lvariants}
    )
    if r:
        return RedirectResponse(
            f"/project/lid/{r}?page={page}&search={search}", status_code=303
        )
    else:
        return RedirectResponse(url, status_code=303)


if __name__ == "__main__":
    import uvicorn

    for route in app.routes:
        print(route.path, route.name)

    uvicorn.run(app, host="127.0.0.1", port=1707, log_level="debug")