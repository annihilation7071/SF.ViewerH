from flask import Flask, render_template, request, send_file, redirect
from backend import utils, downloader
from backend.editor import selector as edit_selector
from backend.projects import Projects
from backend import logger
from backend.processors import general

PROJECTS_PER_PAGE = 60
PPG = PROJECTS_PER_PAGE

logger.start()

general.get_projects()
projects = Projects(ppg=PPG)
projects.update_pools_v()

app = Flask(__name__)


def get_visible_pages(current_page, total_pages):
    if total_pages <= 15:
        return list(range(1, total_pages + 1))

    visible_pages = []
    # Начало страницы
    if current_page > 7:
        visible_pages.append(1)
        visible_pages.append('...')

    # Основной диапазон
    start_page = max(1, current_page - 7)
    end_page = min(total_pages, start_page + 15 - 1)

    if end_page == total_pages:
        start_page = max(1, total_pages - 15 + 1)

    visible_pages.extend(range(start_page, end_page + 1))

    # Конец страницы
    if end_page < total_pages:
        visible_pages.append('...')
        visible_pages.append(total_pages)

    return visible_pages


@app.route('/')
def index():
    global projects

    search_query = request.args.get("search", "").strip().lower()
    print(search_query)
    page = int(request.args.get('page', 1))

    displayed_projects = projects.get_page(page=page, search=search_query)

    total_pages = (projects.len() + PPG - 1) // PPG

    visible_pages = get_visible_pages(page, total_pages)

    return render_template(
        'index.html',
        projects=displayed_projects,
        current_page=page,
        total_pages=total_pages,
        visible_pages=visible_pages,
    )


@app.route('/project/<int:project_id>')
def detail_view(project_id):
    project = projects.get_project_by_id(project_id)
    images = utils.get_pages(project)
    return render_template("detailview.html", project=project, images=images)


@app.route('/project/lid/<string:project_lid>')
def detail_view_lid(project_lid):
    print(project_lid)
    project = projects.get_project_by_lid(project_lid)
    images = utils.get_pages(project)
    return render_template("detailview.html", project=project, images=images)


@app.route('/project/<int:project_id>/<int:page_id>')
def reader(project_id, page_id):
    project = projects.get_project_by_id(project_id)
    images = utils.get_pages(project)
    page = page_id
    image = images[page - 1]["path"]
    total_pages = len(images)
    visible_pages = get_visible_pages(page, total_pages)
    return render_template("reader.html",
                           image=image,
                           current_page=page,
                           project_id=project_id,
                           total_pages=total_pages,
                           visible_pages=visible_pages,
                           )


@app.route('/get_image/<path:image_path>')
def get_image(image_path):
    try:
        if image_path.endswith('.svg'):
            mimetype = 'image/svg+xml'
        else:
            mimetype = 'image/jpeg'

        return send_file(image_path, mimetype=mimetype)
    except FileNotFoundError:
        return "Image not found", 404


@app.route('/items/tags')
def tags_list():
    item = "tag"
    find = item
    tags = projects.count_item(item)
    return render_template("items.html", items=tags, find=find)


@app.route('/items/artists')
def artists_list():
    item = "artist"
    find = item
    tags = projects.count_item(item)
    return render_template("items.html", items=tags, find=find)


@app.route('/items/characters')
def characters_list():
    item = "character"
    find = item
    tags = projects.count_item(item)
    return render_template("items.html", items=tags, find=find)


@app.route('/items/parodies')
def parodies_list():
    item = "parody"
    find = item
    tags = projects.count_item(item)
    return render_template("items.html", items=tags, find=find)


@app.route('/load', methods=['POST'])
def load():
    data = request.json
    print("Received URL:", data.get('url'))
    downloader.download(data.get('url'))
    return {"status": "success"}


@app.route('/edit_data', methods=['POST'])
def update_tags():
    _type = request.form.get('edit-type')
    data = request.form.get('edit-data')
    url = request.form.get('url')
    lid = request.form.get('lid')
    _id = request.form.get('id')
    project = projects.get_project_by_id(int(_id))
    print(project)

    print(_type)
    print(data)
    print(url)
    print(lid)
    print(_id)

    edit_selector.edit(projects, _type, data, project)

    return redirect(url)


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True, use_reloader=False, host='0.0.0.0', port=1707)
