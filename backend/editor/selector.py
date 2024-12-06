from backend.editor import tag_editor


def edit(lid: str, edit_type: str, data: str, projects: list):
    match edit_type:
        case "edit-tags":
            tag_editor.edit(lid, data, projects)
        case _:
            print(f"{edit_type} is not supported")