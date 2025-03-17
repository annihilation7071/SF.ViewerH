from backend.main_import import *


libs: dict[str, Lib] | None = None


class TargetsFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        global libs
        libs = utils.read_libs(check=False, only_active=False)
        targets = utils.read_json(Path("./settings/download/download_targets.json"))

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.list = TargetsList(master=self, targets=targets)
        self.list.grid(row=0, column=0, sticky="nsew")


class TargetsList(customtkinter.CTkScrollableFrame):
    def __init__(self, master: TargetsFrame, targets: dict, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure((0, 1), weight=1)

        self.headers = TargetsListHeaders(master=self)
        self.headers.grid(column=0, row=0, sticky='new', padx=5, pady=5, columnspan=2)

        sites = list(targets.keys())
        for i in range(len(sites)):
            site = sites[i]
            lib_name = targets[site]

            field = TargetsListField(master=self, site=site, lib_name=lib_name)
            field.grid(row=i+1, column=0, sticky="new", padx=5, pady=5, columnspan=2)


class TargetsListHeaders(customtkinter.CTkFrame):
    def __init__(self, master: TargetsList, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure((0, 1), weight=1)

        self.site = customtkinter.CTkLabel(self, text="Site", width=250)
        self.site.grid(row=0, column=0, sticky="new", padx=5, pady=5)

        self.target = customtkinter.CTkLabel(self, text="Target lib", width=350)
        self.target.grid(row=0, column=1, sticky="new", padx=5, pady=5)


class TargetsListField(customtkinter.CTkFrame):
    def __init__(self, master: TargetsList, site: str, lib_name: str, **kwargs):
        super().__init__(master, **kwargs)

        self.site = site

        self.grid_columnconfigure((0, 1), weight=1)

        self.site_label = customtkinter.CTkLabel(self, text=site, width=250)
        self.site_label.grid(row=0, column=0, sticky="new", padx=5, pady=5)

        self.lib_name = customtkinter.CTkOptionMenu(self,
                                                    values=list(libs.keys()),
                                                    width=350,
                                                    command=self.change_target_lib)
        self.lib_name.set(lib_name)
        self.lib_name.grid(row=0, column=1, sticky="new", padx=5, pady=5)

    def change_target_lib(self, *args):
        new_target_lib = self.lib_name.get()

        targets = utils.read_json(Path("./settings/download/download_targets.json"))
        targets[self.site] = new_target_lib

        utils.write_json(Path("./settings/download/download_targets.json"), targets)
