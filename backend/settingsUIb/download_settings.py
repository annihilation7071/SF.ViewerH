import customtkinter
from backend import utils
from pathlib import Path
from backend.classes.lib import Lib
from backend import dep
from backend.classes.dsettings import BaseSettings

dsettings: dict[str, BaseSettings] | None = None


class DSFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        global dsettings
        dsettings = BaseSettings.load()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.list = DSList(master=self)
        self.list.grid(row=0, column=0, sticky="nsew")


class DSList(customtkinter.CTkScrollableFrame):
    def __init__(self, master: DSFrame, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure((0, 1), weight=1)

        self.headers = DSListHeaders(master=self)
        self.headers.grid(column=0, row=0, sticky='new', padx=5, pady=5, columnspan=2)

        downloaders = list(dsettings)
        for i in range(len(downloaders)):
            downloader = dsettings[downloaders[i]]

            field = DSListField(master=self, downloader=downloader)
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
    def __init__(self, master: DSList, downloader: BaseSettings, **kwargs):
        super().__init__(master, **kwargs)

        self.downloader = downloader

        self.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.downloader_name = customtkinter.CTkLabel(self, text=downloader.name, width=150)
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
        if getattr(self.downloader, name) == "N/A":
            return "Not available", "#636467"
        if getattr(self.downloader, name) is None:
            return "Not configured", "#636467"
        return "Configured", "#000000"

