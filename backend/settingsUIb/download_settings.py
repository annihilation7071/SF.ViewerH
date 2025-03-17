from backend.main_import import *
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
            field.grid(row=i + 1, column=0, sticky="new", padx=5, pady=5, columnspan=2)


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

        self.edit_button = customtkinter.CTkButton(self, text="Edit", width=100, command=self._edit)
        self.edit_button.grid(row=0, column=4, padx=5, pady=5)

    def _get_setting(self, name: str) -> tuple[str, str]:
        if getattr(self.downloader, name) == "N/A":
            return "Not available", "#636467"
        if getattr(self.downloader, name) is None:
            return "Not configured", "#636467"
        return "Configured", "#000000"

    def _edit(self):
        editor = Editor(master=self, downloader=self.downloader)
        editor.grab_set()


class Editor(customtkinter.CTkToplevel):
    def __init__(self, master: DSListField, downloader: BaseSettings, **kwargs):
        super().__init__(master, **kwargs)

        self.geometry("800x300")
        self.title("Editor")

        self.downloader = downloader
        self.master = master

        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.fields = EditorFields(master=self, downloader=downloader)
        self.fields.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        self.buttons = EditButtons(master=self)
        self.buttons.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

    def save(self):
        (self.downloader.proxy,
         self.downloader.user_agent,
         self.downloader.cookies) = self.fields.get()

        self.downloader.save()
        dep.settingsUI.renew(active_tab=2)

    def cancel(self):
        self.destroy()


class EditorFields(customtkinter.CTkFrame):
    def __init__(self, master: Editor, downloader: BaseSettings, **kwargs):
        super().__init__(master, **kwargs)

        # self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure((0, 1), weight=1)

        self.downloader = downloader

        # Proxy
        self.proxy_label = customtkinter.CTkLabel(self, text="Proxy")
        self.proxy_label.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        self.proxy_entry = customtkinter.CTkEntry(self, width=500)
        proxy = downloader.proxy if downloader.proxy else ""
        self.proxy_entry.insert(0, proxy)
        self.proxy_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)

        # User-Agent
        self.user_agent_label = customtkinter.CTkLabel(self, text="User-Agent")
        self.user_agent_label.grid(row=1, column=0, sticky='ew', padx=5, pady=5)

        self.user_agent_entry = customtkinter.CTkTextbox(self, width=500, height=50)
        user_agent = downloader.user_agent if downloader.user_agent else ""
        self.user_agent_entry.insert("0.0", user_agent)
        self.user_agent_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

        # Cookies
        text = "Cookies"
        if downloader.name.startswith("gallery-dl"):
            text += "\n(Must be set a file)"
            self.check_cookies_file = True
        else:
            text += "\n(Can be set a file or plain text)"
            self.check_cookies_file = False

        self.cookies_label = customtkinter.CTkLabel(self, text=text, wraplength=100)
        self.cookies_label.grid(row=2, column=0, sticky='ew', padx=5, pady=5)

        cookies = downloader.cookies if downloader.cookies else ""
        self.cookies_selector = CookiesSelector(master=self, width=500, height=100)
        if cookies != "N/A":
            self.cookies_selector.set(cookies)
        else:
            self.cookies_selector.disable()
        self.cookies_selector.grid(row=2, column=1, sticky='ew', padx=5, pady=5)

    def get(self):
        proxy = self.proxy_entry.get()
        if proxy == "":
            proxy = None

        user_agent = self.user_agent_entry.get(0.0, "end")
        user_agent = user_agent.replace("\n", "").replace("\t", "")
        if user_agent == "":
            user_agent = None

        cookies = self.cookies_selector.get()
        cookies = cookies.replace("\n", "").replace("\t", "")
        if cookies == "":
            cookies = None
        else:
            if (self.check_cookies_file and
                    self.downloader.cookies != "N/A" and
                    Path(cookies).exists() is False):
                raise FileNotFoundError(f"Cookies file not found: {cookies}")

        return proxy, user_agent, cookies


class EditButtons(customtkinter.CTkFrame):
    def __init__(self, master: Editor, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure((0, 1), weight=1)

        self.save = customtkinter.CTkButton(self, text="Save", command=master.save)
        self.save.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        self.cancel = customtkinter.CTkButton(self, text="Cancel", command=master.cancel)
        self.cancel.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)


class CookiesSelector(customtkinter.CTkFrame):
    def __init__(self, master: EditorFields, width: int, height: int, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        self.textarea = customtkinter.CTkTextbox(self, width=width - 100, height=height)
        self.textarea.grid(row=0, column=0, sticky='nsew', padx=(0, 5), pady=0)

        self.button = customtkinter.CTkButton(self, text="Choose file", width=100, height=height,
                                              command=self._choose_file)
        self.button.grid(row=0, column=1, sticky='nsew', padx=(5, 0), pady=0)

    def _choose_file(self):
        file = filedialog.askopenfilename(initialdir="/", title="Select file", filetypes=(("Text Files", "*.txt"),))
        self.textarea.delete(0.0, "end")
        self.textarea.insert(0.0, file)

    def set(self, text: str):
        self.textarea.delete(0.0, "end")
        self.textarea.insert(0.0, text)

    def get(self):
        data = self.textarea.get(0.0, "end").replace("\n", "").replace("\t", "")
        if data == "Not available":
            return "N/A"
        return data

    def disable(self):
        self.textarea.delete(0.0, "end")
        self.textarea.insert(0.0, "Not available")
        self.textarea.configure(state="disabled", fg_color="#B2BBBC")
        self.button.configure(state="disabled")
