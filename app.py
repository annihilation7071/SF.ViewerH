from flask import Flask, render_template, request, send_file
from backend import search, utils

# all_projects = []
projects = {'search': "",
            'data': []}


all_projects = utils.get_projects()
projects['search'] = ""
projects['data'] = all_projects

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
    global all_projects
    global projects

    if len(all_projects) == 0:
        all_projects = utils.get_projects()
        projects['search'] = ""
        projects['data'] = all_projects

    search_query = request.args.get("search", "").strip().lower()
    print(search_query)
    if search_query == projects['search']:
        _projects = projects['data']
    else:
        projects['search'] = search_query
        projects['data'] = search.to_search(all_projects, search_query)
        _projects = projects['data']

    page = int(request.args.get('page', 1))
    start_index = (page - 1) * 25
    end_index = start_index + 25

    displayed_projects = _projects[start_index:end_index]

    total_pages = (len(_projects) + 25 - 1) // 25

    visible_pages = get_visible_pages(page, total_pages)

    return render_template(
        'index.html',
        mangas=displayed_projects,
        current_page=page,
        total_pages=total_pages,
        visible_pages=visible_pages,
    )


@app.route('/manga/<int:project_id>')
def detail_view(project_id):
    project = all_projects[project_id]
    images = utils.get_pages(project)
    # print(project)
    # print(images)
    return render_template("detailview.html", manga=project, images=images)


@app.route('/manga/<int:project_id>/<int:page_id>')
def reader(project_id, page_id):
    project = all_projects[project_id]
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
        return send_file(image_path, mimetype='image/jpeg')
    except FileNotFoundError:
        return "Image not found", 404


@app.route('/items/tags')
def tags_list():
    item = "tag"
    find = item
    tags = utils.count_param(item, all_projects)
    return render_template("items.html", items=tags, find=find)


@app.route('/items/artists')
def artists_list():
    item = "artist"
    find = item
    tags = utils.count_param(item, all_projects)
    return render_template("items.html", items=tags, find=find)


@app.route('/items/characters')
def characters_list():
    item = "character"
    find = item
    tags = utils.count_param(item, all_projects)
    return render_template("items.html", items=tags, find=find)


@app.route('/items/parodies')
def parodies_list():
    item = "parody"
    find = item
    tags = utils.count_param(item, all_projects)
    return render_template("items.html", items=tags, find=find)


@app.route('/load', methods=['POST'])
def load():
    data = request.json
    print("Received URL:", data.get('url'))
    return {"status": "success"}


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True, host='0.0.0.0', port=5000)