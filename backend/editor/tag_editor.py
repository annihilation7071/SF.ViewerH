from backend.utils import tag_normalizer
from backend.editor import eutils


def edit(projects, data: str, project):
    print("edit-tags")

    tags = data.split("\n")
    print(tags)
    tags = [tag for tag in tags if tag != ""]
    tags = tag_normalizer(tags)
    print(tags)

    eutils.update_data(projects, project, "tag", tags)

    return
