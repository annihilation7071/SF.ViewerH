from backend.editor import item_editor, variants_editor


def edit(projects, project: dict, edit_type: str, data: str, extra: dict = None):
    match edit_type:
        case "edit-tags" | "edit-series":
            return item_editor.edit(projects, project, edit_type, data)
        case "edit-variants":
            return variants_editor.edit(projects, project, data)
        case _:
            print(edit_type)
            print(data)
            print(f"{edit_type} is not supported")