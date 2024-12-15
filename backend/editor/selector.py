from backend.editor import tag_editor, variants_editor


def edit(projects, edit_type: str, data: str, project: dict, extra: dict = None):
    print("-----EDIT-----")
    match edit_type:
        case "edit-tags":
            return tag_editor.edit(projects, data, project)
        case "edit-variants":
            return variants_editor.edit(projects, data, extra["lvariants"])
        case _:
            print(edit_type)
            print(data)
            print(f"{edit_type} is not supported")
    print("---END_EDIT---")