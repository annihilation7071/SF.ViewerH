from backend.editor import tag_editor


def edit(edit_type: str, data: str, project: dict):
    print("-----EDIT-----")
    match edit_type:
        case "edit-tags":
            tag_editor.edit(data, project)
        case _:
            print(edit_type)
            print(data)
            print(f"{edit_type} is not supported")
    print("---END_EDIT---")