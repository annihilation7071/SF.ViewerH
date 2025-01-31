import customtkinter
from backend.settingsUI.libs import LibsFrame
from backend.settingsUI.targets import TargetsFrame
from backend.modules import logger

log = logger.get_logger("SenntinsUI.mainframe")


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

        self.dttab.grid_columnconfigure((0, 1), weight=1)
        self.dttab.grid_rowconfigure((0, 1), weight=1)

        self.libsframe = LibsFrame(master=self.libstab)
        self.libsframe.grid(row=0, column=0, sticky="nsew", rowspan=2, columnspan=2)

        self.targetsframe = TargetsFrame(master=self.dttab)
        self.targetsframe.grid(row=0, column=0, sticky="nsew", rowspan=2, columnspan=2)

    def renew(self):
        log.debug("renew")

        self.libsframe.destroy()
        self.libsframe = LibsFrame(master=self.libstab)
        self.libsframe.grid(row=0, column=0, sticky="nsew", rowspan=2, columnspan=2)

        # self.dttab.destroy()
        # self.dttab = TargetsFrame(master=self.dttab)
        # self.dttab.grid(row=0, column=0, sticky="nsew", rowspan=2, columnspan=2)


