import json
import os

from backend.projects import Projects
from backend.processors.general import tag_normalizer
from backend.editor import eutils

projects = Projects()


def edit(data: str, project):
    print("edit-tags")

    tags = data.split("\n")
    print(tags)
    tags = [tag for tag in tags if tag != ""]
    tags = tag_normalizer(tags)
    print(tags)

    eutils.update_data(project, "tag", tags)

    return

