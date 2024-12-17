from quart import Quart, render_template, request, send_file, redirect, jsonify
from backend import utils, downloader
from backend.editor import selector as edit_selector
from backend.projects import Projects
from backend import logger

PROJECTS_PER_PAGE = 60
PPG = PROJECTS_PER_PAGE

logger.start()

projects = Projects()
projects.update_projects()

app = Quart(__name__)


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


@app.route('/')
async def index():
    search_query = request.args.get("search", "").strip().lower()
    page = int(request.args.get('page', 1))

    displayed_projects = projects.get_page(PPG, page=page, search=search_query)
    total_pages = (projects.len() + PPG - 1) // PPG
    visible_pages = get_visible_pages(page, total_pages)

    return await render_template(
        'index.html',
        projects=displayed_projects,
        current_page=page,
        total_pages=total_pages,
        visible_pages=visible_pages,
    )


@app.route('/project/<int:project_id>')
async def detail_view(project_id):
    project = projects.get_project_by_id(project_id)
    images = utils.get_pages(project)
    return await render_template("detailview.html", project=project, images=images)


@app.route('/project/lid/<string:project_lid>')
async def detail_view_lid(project_lid):
    project = projects.get_project_by_lid(project_lid)
    images = utils.get_pages(project)
    return await render_template("detailview.html", project=project, images=images)


@app.route('/project/<int:project_id>/<int:page_id>')
async def reader(project_id, page_id):
    project = projects.get_project_by_id(project_id)
    images = utils.get_pages(project)
    page = page_id
    image = images[page - 1]["path"]
    total_pages = len(images)
    visible_pages = get_visible_pages(page, total_pages)
    return await render_template(
        "reader.html",
        image=image,
        current_page=page,
        project_id=project_id,
        total_pages=total_pages,
        visible_pages=visible_pages,
    )


@app.route('/get_image/<path:image_path>')
async def get_image(image_path):
    try:
        mimetype = 'image/svg+xml' if image_path.endswith('.svg') else 'image/jpeg'
        return await send_file(image_path, mimetype=mimetype)
    except FileNotFoundError:
        return "Image not found", 404


@app.route('/items/tags')
async def tags_list():
    item = "tag"
    tags = projects.count_item(item)
    return await render_template("items.html", items=tags, find=item)


@app.route('/items/artists')
async def artists_list():
    item = "artist"
    tags = projects.count_item(item)
    return await render_template("items.html", items=tags, find=item)


@app.route('/items/characters')
async def characters_list():
    item = "character"
    tags = projects.count_item(item)
    return await render_template("items.html", items=tags, find=item)


@app.route('/items/parodies')
async def parodies_list():
    item = "parody"
    tags = projects.count_item(item)
    return await render_template("items.html", items=tags, find=item)


@app.route('/load', methods=['POST'])
async def load():
    data = await request.json
    print("Received URL:", data.get('url'))
    downloader.download(data.get('url'))
    return jsonify({"status": "success"})


@app.route('/edit_data', methods=['POST'])
async def update_tags():
    form = await request.form
    _type = form.get('edit-type')
    data = form.get('edit-data')
    url = form.get('url')
    lid = form.get('lid')
    _id = form.get('id')
    page = form.get('page')
    search = form.get('search')
    lvariants = form.get('lvariants')

    project = projects.get_project_by_id(int(_id))
    print(project, _type, data, url, lid, _id)

    r = edit_selector.edit(projects, _type, data, project, extra={"lvariants": lvariants})
    if r:
        return redirect(f"/project/lid/{r}?page={page}&search={search}")
    else:
        return redirect(url)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, host='127.0.0.1', port=1707)
