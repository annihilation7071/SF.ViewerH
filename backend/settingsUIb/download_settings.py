import customtkinter
from backend import utils
from pathlib import Path
from backend.classes.lib import Lib
from backend import dep


class DSFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        ds: dict[str, dict] = utils.read_json(Path("./settings/download/settings.json"))

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.list = DSList(master=self, ds=ds)
        self.list.grid(row=0, column=0, sticky="nsew")


class DSList(customtkinter.CTkScrollableFrame):
    def __init__(self, master: DSFrame, ds: dict[str, dict], **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure((0, 1), weight=1)

        self.headers = DSListHeaders(master=self)
        self.headers.grid(column=0, row=0, sticky='new', padx=5, pady=5, columnspan=2)

        downloaders = list(ds.keys())
        for i in range(len(downloaders)):
            downloader = downloaders[i]
            downloader_s = ds[downloader]

            field = DSListField(master=self, downloader=downloader, downloader_s=downloader_s)
            field.grid(row=i+1, column=0, sticky="new", padx=5, pady=5, columnspan=2)


class DSListHeaders(customtkinter.CTkFrame):
    def __init__(self, master: DSList, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.site = customtkinter.CTkLabel(self, text="Downloader", width=150)
        self.site.grid(row=0, column=0, sticky="new", padx=5, pady=5)

        self.target = customtkinter.CTkLabel(self, text="Proxy", width=150)
        self.target.grid(row=0, column=1, sticky="new", padx=5, pady=5)

        self.user_anget = customtkinter.CTkLabel(self, text="User-Agent", width=100)
        self.user_anget.grid(row=0, column=2, sticky="new", padx=5, pady=5)

        self.cookies = customtkinter.CTkLabel(self, text="Cookies", width=100)
        self.cookies.grid(row=0, column=3, sticky="new", padx=5, pady=5)

        self.empty = customtkinter.CTkLabel(self, text="", width=100)
        self.empty.grid(row=0, column=4, sticky="new", padx=5, pady=5)


class DSListField(customtkinter.CTkFrame):
    def __init__(self, master: DSList, downloader: str, downloader_s: dict, **kwargs):
        super().__init__(master, **kwargs)

        self.downloader = downloader
        self.downloader_s = downloader_s

        self.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.downloader_name = customtkinter.CTkLabel(self, text=downloader, width=150)
        self.downloader_name.grid(row=0, column=0, sticky="new", padx=5, pady=5)

        proxy, tc = self._get_setting("proxy")
        self.proxy_name = customtkinter.CTkLabel(self, text=proxy, width=150, text_color=tc)
        self.proxy_name.grid(row=0, column=1, sticky="new", padx=5, pady=5)

        user_agent, tc = self._get_setting("user_agent")
        self.user_anget = customtkinter.CTkLabel(self, text=user_agent, width=100, text_color=tc)
        self.user_anget.grid(row=0, column=2, sticky="new", padx=5, pady=5)

        cookies, tc = self._get_setting("cookies")
        self.cookies = customtkinter.CTkLabel(self, text=cookies, width=100, text_color=tc)
        self.cookies.grid(row=0, column=3, sticky="new", padx=5, pady=5)

        self.edit_button = customtkinter.CTkButton(self, text="Edit", width=100)
        self.edit_button.grid(row=0, column=4, padx=5, pady=5)

    def _get_setting(self, name: str) -> tuple[str, str]:
        if name not in self.downloader_s:
            return "Not available", "#636467"
        if self.downloader_s[name] is None:
            return "Not configured", "#636467"
        # if name == "proxy":
        #     return self.downloader_s[name]
        return "Configured", "#000000"

    # def change_target_lib(self, *args):
    #     new_target_lib = self.lib_name.get()
    #
    #     targets = utils.read_json(Path("./settings/download/download_targets.json"))
    #     targets[self.site] = new_target_lib
    #
    #     utils.write_json(Path("./settings/download/download_targets.json"), targets)
