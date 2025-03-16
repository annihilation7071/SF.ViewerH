from backend.main_import import *
from backend.utils import *
from backend.settingsUIb.mainframe import MainFrame
from backend import init
from backend import dep


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("SF.ViewerH Settings")
        self.geometry("800x500+500+400")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.mainframe = MainFrame(self)
        self.mainframe.grid(column=0, row=0, padx=10, pady=(0, 10), sticky="nsew")

    def renew(self, active_tab: int = 0):
        self.mainframe.destroy()
        self.mainframe = MainFrame(self, active_tab=active_tab)
        self.mainframe.grid(column=0, row=0, padx=10, pady=(0, 10), sticky="nsew")


if __name__ == '__main__':
    init.init()
    app = App()
    dep.settingsUI = app
    app.mainloop()