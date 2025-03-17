# https://github.com/mikf/gallery-dl
# --write-info-json

from backend.main_import import *

log = logger.get_logger("Processor.gallery-dl-nhentai")

meta_file = "info.json"


def parse(path: Path, template: ProjectBase) -> ProjectBase:
    log.debug("gallery-dl-nhentai.parse")

    with open(os.path.join(path, meta_file), "r", encoding='utf-8') as f:
        metadata = defaultdict(lambda: False, json.load(f))

    template.source = "nhentai.net"
    template.downloader = "gallery-dl"

    files = os.listdir(path)
    files = [file for file in files if file.startswith("nhentai_")]
    files = sorted(files)
    template.preview = files[0]

    _name = os.path.basename(path)

    # noinspection PyBroadException
    try:
        if metadata["gallery_id"] is not False:
            _id = metadata["gallery_id"]
            template.source_id = str(_id)
        else:
            try:
                _id = _name[0:_name.find(" ")]
                _id = int(_id)
            except Exception as e:
                _id = _name
                _id = int(_id)
                raise e
            template.source_id = str(_id)
    except Exception:
        template.source_id = "unknown"

    template.url = "unknown"
    template.title = metadata["title"] or metadata["title_en"] or _name
    template.subtitle = metadata["title_ja"] or metadata["title_en"] or ""
    if template.title == template.subtitle:
        template.subtitle = ""
    # noinspection PyTypeChecker
    template.upload_date = utils.to_time(metadata["date"]) or datetime.now()
    template.category = ["unknown"]
    template.series = []

    def f(key: str) -> list | str:
        return utils.tag_normalizer(metadata[key])

    template.parody = f("parody") or ["unknown"]
    template.character = f("characters") or ["unknown"]
    template.tag = f("tags") or ["unknown"]
    template.artist = f("artist") or ["unknown"]
    template.group = f("group") or ["unknown"]
    template.language = [f("language")] or ["unknown"]
    template.pages = f("count") or -1

    return template
