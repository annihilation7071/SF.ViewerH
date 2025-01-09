# import json
# from backend.classes.projecte import ProjectE
# from backend.logger_new import get_logger
#
# log = get_logger("Eutils")
#
#
# def update_data(projects,
#                 project: ProjectE,
#                 target: str | list,
#                 new_data,
#                 multiple: bool = False,
#                 update_priority: bool = True):
#     # v_info.json
#     path = project.path / "sf.viewer/v_info.json"
#
#     if multiple is False:
#         target = [target]
#         new_data = [new_data]
#
#     # Open
#     with open(path, "r", encoding="utf-8") as f:
#         v_info = json.load(f)
#
#     # Update
#     for i in range(0, len(target)):
#         if target[i] in v_info:
#             v_info[target[i]] = new_data[i]
#
#     # Save
#     with open(path, "w", encoding="utf-8") as f:
#         # noinspection PyTypeChecker
#         json.dump(v_info, f, indent=4)
#
#     # DB
#     for i in range(0, len(target)):
#         setattr(project, target[i], new_data[i])
#
#     projects.update_item(project)
#     if len(project["lvariants"]) and update_priority is True:
#         projects.update_priority(project)


# def update_data_2(projects, project: dict):
#     target_columns = list(project.keys())
#     new_data = list(project.values())
#     update_data(projects, project, target_columns, new_data, multiple=True)