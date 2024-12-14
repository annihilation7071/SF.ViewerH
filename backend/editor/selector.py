from backend.editor import tag_editor, variants_editor


def edit(projects, edit_type: str, data: str, project: dict):
    print("-----EDIT-----")
    match edit_type:
        case "edit-tags":
            tag_editor.edit(projects, data, project)
        case "edit-variants":
            variants_editor.edit(projects, data)
        case _:
            print(edit_type)
            print(data)
            print(f"{edit_type} is not supported")
    print("---END_EDIT---")