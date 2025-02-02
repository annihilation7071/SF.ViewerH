import os.path

import customtkinter
from tkinter import *
from tkinter import ttk
from backend import utils
from backend.classes.lib import Lib
from pathlib import Path
from backend.settingsUIb.general import SelectFolder
from backend import dep


class LibsFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.table = LibsList(self)
        self.table.grid(row=0, column=0, sticky='nsew')


class LibsList(customtkinter.CTkScrollableFrame):
    def __init__(self, master: LibsFrame, **kwargs):
        super().__init__(master, **kwargs)

        self.master = master

        self.grid_columnconfigure(0, weight=1)

        libs = utils.read_libs(check=False, only_active=False)

        self.headers = Headers(master=self)

        for i in range(len(libs)):
            row = LibField(master=self, lib=list(libs.values())[i])
            row.grid(row=i + 1, column=0, sticky='ew', padx=5, pady=5)

    def create(self):
        new_lib = Lib(
            libfile=Path("./settings/libs/libs_user.json"),
            processor="none",
            active=True,
            name="",
            path=Path("")
        )

        editor = Editor(master=self, lib=new_lib, mode="create")
        editor.grab_set()


class Headers(customtkinter.CTkFrame):
    def __init__(self, master: LibsList, **kwargs):
        super().__init__(master, **kwargs)

        self.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
    
        self.header_1 = customtkinter.CTkLabel(
            self, text="Lib name", anchor="w", width=300
        )
        self.header_1.grid(row=0, column=0, sticky='w', padx=5, pady=5)
    
        self.header_2 = customtkinter.CTkLabel(
            self, text="Processor", width=200, anchor="center"
        )
        self.header_2.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
    
        self.header_3 = customtkinter.CTkLabel(
            self, text="Active", width=50, anchor="w"
        )
        self.header_3.grid(row=0, column=2, sticky='ew', padx=5, pady=5)
    
        self.header_4 = customtkinter.CTkButton(
            self, text="Add lib", width=100, command=master.create, fg_color="#4179BC"
        )
        self.header_4.grid(row=0, column=3, sticky='e', padx=5, pady=5)


class LibField(customtkinter.CTkFrame):
    def __init__(self, master: LibsList, lib: Lib, **kwargs):
        super().__init__(master, **kwargs)

        self.columnconfigure((0, 1, 2, 3), weight=1)

        self.lib = lib
        self.master = master

        # Lib name
        self.label_1 = customtkinter.CTkLabel(
            self,
            text=utils.truncate_text(lib.name, 40),
            anchor="w",
            width=300,
        )
        self.label_1.grid(row=0, column=0, sticky='w', padx=5, pady=5)

        # Processor
        self.label_2 = customtkinter.CTkLabel(
            self,
            text=utils.truncate_text(lib.processor, 30),
            width=200,
            anchor="center",
            # bg_color="light blue",
        )
        self.label_2.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

        # Status
        self.status = customtkinter.CTkCheckBox(
            self,
            width=50,
            text="",
            command=self.set_status
        )
        self.status.grid(row=0, column=2, sticky='ew', padx=5, pady=5)
        if lib.active:
            self.status.select()
        else:
            self.status.deselect()

        # Button
        self.button = customtkinter.CTkButton(self, text="Edit", command=self.edit, width=100)
        self.button.grid(row=0, column=3, sticky='e', padx=5, pady=5)

        if lib.libfile.name == "libs_default.json":
            self.button.configure(state=DISABLED)

    def edit(self):
        editor = Editor(master=self, lib=self.lib, mode="edit")
        editor.grab_set()

    def set_status(self, *args):
        self.lib.active = bool(self.status.get())
        self.lib.save()


class Editor(customtkinter.CTkToplevel):
    def __init__(self, master: LibField | LibsList, mode, lib: Lib, **kwargs):
        super().__init__(master, **kwargs)

        self.geometry("800x300")
        self.title("Editor")

        self.lib = lib
        self.master = master

        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.labels = EditorFields(master=self, lib=lib, mode=mode)
        self.labels.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        self.buttons = EditButtons(master=self, mode=mode)
        self.buttons.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

    def save(self):
        lib = self.labels.get()
        lib.save()
        self.cancel()
        dep.settingsUI.renew()

    def create(self):
        lib = self.labels.get()
        lib.create()
        self.cancel()
        dep.settingsUI.renew()

    def delete(self):
        lib = self.labels.get()
        lib.delete()
        self.cancel()
        dep.settingsUI.renew()

    def cancel(self):
        self.destroy()


class EditorFields(customtkinter.CTkFrame):
    def __init__(self, master: Editor, lib: Lib, mode, **kwargs):
        super().__init__(master, **kwargs)

        # self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        # Lib file
        self.libfile = customtkinter.CTkLabel(self, text="Lib file")
        self.libfile.grid(row=0, column=0, sticky='w', padx=5, pady=5)

        self.libfile_entry = customtkinter.CTkEntry(self, width=500)
        self.libfile_entry.insert(0, os.path.splitext(lib.libfile.name)[0])
        self.libfile_entry.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        if mode == "edit":
            self.libfile_entry.configure(state=DISABLED, fg_color="#B2BBBC")

        # Name
        self.name = customtkinter.CTkLabel(self, text="Name")
        self.name.grid(row=1, column=0, sticky='w', padx=5, pady=5)

        self.name_entry = customtkinter.CTkEntry(self, width=500)
        self.name_entry.insert(0, lib.name)
        self.name_entry.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)

        if mode == "edit":
            self.name_entry.configure(state=DISABLED, fg_color="#B2BBBC")

        # Status
        self.active = customtkinter.CTkLabel(self, text="Active")
        self.active.grid(row=2, column=0, sticky='w', padx=5, pady=5)

        self.active_checkbox = customtkinter.CTkCheckBox(self, text="")
        if lib.active:
            self.active_checkbox.select()
        else:
            self.active_checkbox.deselect()
        self.active_checkbox.grid(row=2, column=1, sticky='nsew', padx=5, pady=5)

        # Processor
        self.processor = customtkinter.CTkLabel(self, text="Processor")
        self.processor.grid(row=3, column=0, sticky='w', padx=5, pady=5)

        processors = os.listdir(Path("./backend/processors"))
        processors = [os.path.splitext(processor)[0] for processor in processors]
        processors = [processor for processor in processors if processor.startswith("__") is False]
        self.processor_menu = customtkinter.CTkOptionMenu(
            self,
            values=processors,
        )
        self.processor_menu.set(lib.processor)
        self.processor_menu.grid(row=3, column=1, sticky='nsew', padx=5, pady=5)

        # Path
        self.path = customtkinter.CTkLabel(self, text="Path")
        self.path.grid(row=4, column=0, sticky='w', padx=5, pady=5)

        self.path_entry = SelectFolder(self, width=20)
        self.path_entry.set(lib.path)
        self.path_entry.grid(row=4, column=1, sticky='nsew', padx=5, pady=5)

    def get(self) -> Lib:
        lib = Lib(
            libfile=Path(f"./settings/libs/{self.libfile_entry.get()}.json"),
            name=self.name_entry.get(),
            processor=self.processor_menu.get(),
            active=bool(self.active_checkbox.get()),
            path=Path(self.path_entry.get())
        )
        return lib


class EditButtons(customtkinter.CTkFrame):
    def __init__(self, master: Editor, mode, **kwargs):
        super().__init__(master, **kwargs)

        self.cancel = customtkinter.CTkButton(self, text="Cancel", command=master.cancel)
        self.cancel.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)

        if mode == "edit":
            self.grid_columnconfigure((0, 1, 2), weight=1)
            self.save = customtkinter.CTkButton(self, text="Save", command=master.save)
            self.save.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
            self.delete = customtkinter.CTkButton(self, text="Delete", fg_color="#6B1917", command=master.delete)
            self.delete.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        elif mode == "create":
            self.grid_columnconfigure((0, 1), weight=1)
            self.create = customtkinter.CTkButton(self, text="Create", command=master.create)
            self.create.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
            self.cancel.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
