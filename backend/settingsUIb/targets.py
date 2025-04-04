from backend.main_import import *


libs: Libs | None = None
targets: DownloadersTargets | None = None


class TargetsFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        global libs
        global targets
        libs = Libs.load()
        targets = DownloadersTargets.load()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.list = TargetsList(master=self)
        self.list.grid(row=0, column=0, sticky="nsew")


class TargetsList(customtkinter.CTkScrollableFrame):
    def __init__(self, master: TargetsFrame, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure((0, 1), weight=1)

        self.headers = TargetsListHeaders(master=self)
        self.headers.grid(column=0, row=0, sticky='new', padx=5, pady=5, columnspan=2)

        targets_list = targets.get_list_targets()
        for i in range(len(targets_list)):
            target = targets_list[i]

            field = TargetsListField(master=self, target=target)
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
    def __init__(self, master: TargetsList, target: DownloaderTarget, **kwargs):
        super().__init__(master, **kwargs)

        self.target = target

        self.grid_columnconfigure((0, 1), weight=1)

        self.site_label = customtkinter.CTkLabel(self, text=target.site, width=250)
        self.site_label.grid(row=0, column=0, sticky="new", padx=5, pady=5)

        self.lib_name = customtkinter.CTkOptionMenu(self,
                                                    values=libs.get_names(),
                                                    width=350,
                                                    command=self.change_target_lib)
        self.lib_name.set(target.lib)
        self.lib_name.grid(row=0, column=1, sticky="new", padx=5, pady=5)

    def change_target_lib(self, *args):
        new_target_lib = self.lib_name.get()

        self.target.lib = new_target_lib
        targets.save()

