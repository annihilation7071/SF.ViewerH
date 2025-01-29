import customtkinter
from tkinter import *
from tkinter import ttk
from backend import utils
from backend.classes.lib import Lib


class LibsFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.table = LibsList(self)
        self.table.grid(row=0, column=0, sticky='nsew')

        # self.label = customtkinter.CTkLabel(self, text="test")
        # self.label.grid(row=0, column=2, sticky='nsew')


# class Table(customtkinter.CTkFrame):
#     def __init__(self, master, **kwargs):
#         super().__init__(master, **kwargs)
#
#         self.grid_rowconfigure(0, weight=1)
#         self.grid_columnconfigure(0, weight=1)
#
#         temp_columnt = ["Lib name", "Downloader", "Active"]
#         temp_data = [["Example_lib_1", "Example_downloader_1", True],
#                      ["Example_lib_2", "Example_downloader_2", True],
#                      ["Example_lib_3", "Example_downloader_3", True],]
#
#         self.table = ttk.Treeview(self, columns=temp_columnt, show="headings")
#         self.table.grid(row=0, column=0, sticky="nsew")
#
#         for lib in temp_data:
#             self.table.insert("", "end", values=lib)


class LibsList(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)

        libs = utils.read_libs(check=False, only_active=False)

        self.make_headers()

        for i in range(len(libs)):
            row = LibField(master=self, lib=list(libs.values())[i])
            row.grid(row=i+1, column=0, sticky='ew', padx=5, pady=5)

    def make_headers(self):
        headers = customtkinter.CTkFrame(self)
        headers.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        headers.grid_columnconfigure((0, 1, 2, 3), weight=1)

        headers.header_1 = customtkinter.CTkLabel(
            headers, text="Lib name", anchor="w", width=300
        )
        headers.header_1.grid(row=0, column=0, sticky='w', padx=(5, 25), pady=5)

        headers.header_2 = customtkinter.CTkLabel(
            headers, text="Processor", width=200, anchor="center"
        )
        headers.header_2.grid(row=0, column=1, sticky='ew', padx=(25, 5), pady=5)

        headers.header_3 = customtkinter.CTkLabel(
            headers, text="Active", width=100, anchor="center"
        )
        headers.header_3.grid(row=0, column=2, sticky='ew', padx=(5, 0), pady=5)

        headers.header_4 = customtkinter.CTkButton(
            headers, text="Add lib", width=117
        )
        headers.header_4.grid(row=0, column=3, sticky='e', padx=(0, 5), pady=5)


class LibField(customtkinter.CTkFrame):
    def __init__(self, master, lib: Lib, **kwargs):
        super().__init__(master, **kwargs)

        self.columnconfigure((0, 1, 2), weight=1)

        self.label_1 = customtkinter.CTkLabel(
            self,
            text=utils.truncate_text(lib.name, 40),
            anchor="w",
            width=300,
        )
        self.label_1.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.label_2 = customtkinter.CTkLabel(
            self,
            text=utils.truncate_text(lib.processor, 30),
            width=200,
            anchor="center",
            # bg_color="light blue",
        )
        self.label_2.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self.label_3 = customtkinter.CTkLabel(
            self,
            text=str(lib.active),
            width=50,
            anchor="center",
        )
        self.label_3.grid(row=0, column=2, sticky='ew', padx=5, pady=5)
        self.button = customtkinter.CTkButton(self, text="Edit", command=self.edit, width=100)
        self.button.grid(row=0, column=3, sticky='e', padx=5, pady=5)

    def edit(self):
        editor = Editor(master=self)


class Editor(customtkinter.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.geometry("400x800")
        self.title("Editor")

        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.labels = LibLabels(master=self)
        self.labels.grid(row=0, column=0, sticky='nsew')


class LibLabels(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        self.name = customtkinter.CTkLabel(self, text="Name")
        self.name.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        self.name_entry = customtkinter.CTkEntry(self, width=20)
        self.name_entry.insert(0, "temp")
        self.name_entry.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        self.active = customtkinter.CTkLabel(self, text="Active")
        self.active.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        self.active_checkbox = customtkinter.CTkCheckBox(self, text="")
        self.active_checkbox.select()
        self.active_checkbox.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)

        self.processor = customtkinter.CTkLabel(self, text="Processor")
        self.processor.grid(row=2, column=0, sticky='nsew', padx=5, pady=5)

        self.processor_menu = customtkinter.CTkOptionMenu(
            self,
            values=["Example_downloader_1", "Example_downloader_2", "Example_downloader_3"],
        )
        self.processor_menu.grid(row=2, column=1, sticky='nsew', padx=5, pady=5)

        self.path = customtkinter.CTkLabel(self, text="Path")
        self.path.grid(row=3, column=0, sticky='nsew', padx=5, pady=5)

        self.path_entry = customtkinter.CTkEntry(self, width=20)
        self.path_entry.insert(0, "temp")
        self.path_entry.grid(row=3, column=1, sticky='nsew', padx=5, pady=5)



