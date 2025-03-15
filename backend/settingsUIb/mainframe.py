import customtkinter
from backend.settingsUIb.libs import LibsFrame
from backend.settingsUIb.targets import TargetsFrame
from backend.settingsUIb.download_settings import DSFrame
from backend.utils import logger

log = logger.get_logger("SenntinsUI.mainframe")


class MainFrame(customtkinter.CTkTabview):
    def __init__(self, master, active_tab=0, **kwargs):
        super().__init__(master, **kwargs)

        # self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)

        self.libstab = self.add("Libs")
        self.dttab = self.add("Downloaders Targets")
        self.dstab = self.add("Downloaders Settings")

        # Activate selected tab, default 0.
        self.set(self._name_list[active_tab])

        self.libstab.grid_columnconfigure((0, 1), weight=1)
        self.libstab.grid_rowconfigure((0, 1), weight=1)

        self.dttab.grid_columnconfigure((0, 1), weight=1)
        self.dttab.grid_rowconfigure((0, 1), weight=1)

        self.dstab.grid_columnconfigure((0, 1), weight=1)
        self.dstab.grid_rowconfigure((0, 1), weight=1)

        self.libsframe = LibsFrame(master=self.libstab)
        self.libsframe.grid(row=0, column=0, sticky="nsew", rowspan=2, columnspan=2)

        self.targetsframe = TargetsFrame(master=self.dttab)
        self.targetsframe.grid(row=0, column=0, sticky="nsew", rowspan=2, columnspan=2)

        self.dsframe = DSFrame(master=self.dstab)
        self.dsframe.grid(row=0, column=0, sticky="nsew", rowspan=2, columnspan=2)

    # def renew(self):
    #     log.debug("renew")
    #
    #     self.libsframe.destroy()
    #     self.libsframe = LibsFrame(master=self.libstab)
    #     self.libsframe.grid(row=0, column=0, sticky="nsew", rowspan=2, columnspan=2)
    #
    #     # self.dttab.destroy()
    #     # self.dttab = TargetsFrame(master=self.dttab)
    #     # self.dttab.grid(row=0, column=0, sticky="nsew", rowspan=2, columnspan=2)


