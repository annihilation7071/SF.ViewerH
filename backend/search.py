from dataclasses import dataclass


@dataclass
class SearchBody:
    title: str
    id: str
    parody: str
    character: str
    artist: str
    group: str
    language: str
    tag: str
    category: str
    lib: str
    general: str = None

    def init_general(self):
        attr = vars(self)
        attr.pop('general')
        self.general = ", ".join(attr.values())


def find(search_body: SearchBody, search_items: list | tuple) -> bool:
    for i in range(0, len(search_items)):
        search_item = search_items[i]

        if search_item.find(':') == -1 or search_item.find('general:') != -1:
            if search_body.general.find(search_item.replace('general:', '')) == -1:
                break
        else:
            cat, word = search_item.split(':')
            if getattr(search_body, cat).find(word) == -1:
                break

        if i == len(search_items) - 1:
            return True
    return False


def to_search(projects, search_query):
    _projects = []
    for project in projects:

        def f(item: str):
            if isinstance(project[item], (str | int)) is True:
                return str(project[item]).lower()
            elif isinstance(project[item], (list | tuple)) is True:
                return ", ".join(project[item]).lower()

        search_body = SearchBody(
            title=f"{f('title')}, {f('subtitle')}",
            id=f('id'),
            parody=f('parody'),
            character=f('character'),
            artist=f('artist'),
            group=f('group'),
            language=f('language'),
            tag=f('tag'),
            category=f('category'),
            lib=f('lib')
        )

        search_body.init_general()

        search_items = search_query.split(",")
        search_items = [item.lower().strip() for item in search_items]

        if find(search_body, search_items) is True:
            _projects.append(project)

    return _projects

