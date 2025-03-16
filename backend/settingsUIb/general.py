from backend.main_import import *
from backend.utils import *


class SelectFolder(customtkinter.CTkFrame):
    def __init__(self, *args,
                 width: int = 200,
                 height: int = 32,
                 **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.entry = customtkinter.CTkEntry(self)
        self.entry.grid(row=0, column=0, sticky='ew')

        self.button = customtkinter.CTkButton(self, text="Browse", width=30, command=self.browse)
        self.button.grid(row=0, column=1, sticky='w')

    def browse(self):
        initdir = Path(self.get())
        folder_path = filedialog.askdirectory(initialdir=initdir)
        if folder_path:
            self.entry.delete(0, "end")
            self.entry.insert(0, folder_path)

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)