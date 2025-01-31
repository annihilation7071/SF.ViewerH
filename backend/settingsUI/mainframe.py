import customtkinter
from backend.settingsUI.libs import LibsFrame


class MainFrame(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)

        self.libstab = self.add("Libs")
        self.dttab = self.add("Downloaders Targets")
        self.dstab = self.add("Downloaders Settings")

        self.libstab.grid_columnconfigure((0, 1), weight=1)
        self.libstab.grid_rowconfigure((0, 1), weight=1)

        self.libsframe = LibsFrame(master=self.libstab)
        self.libsframe.grid(row=0, column=0, sticky="nsew", rowspan=2, columnspan=2)


    def renew(self):
        self.libsframe.destroy()
        self.libsframe = LibsFrame(master=self.libstab)
        self.libsframe.grid(row=0, column=0, sticky="nsew", rowspan=2, columnspan=2)


