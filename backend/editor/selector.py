from backend.editor import tag_editor


def edit(edit_type: str, data: str, project: dict):
    match edit_type:
        case "edit-tags":
            tag_editor.edit(data, project)
        case _:
            print(f"{edit_type} is not supported")