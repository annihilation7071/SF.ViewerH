import customtkinter
from backend.settingsUI.mainframe import MainFrame
from backend import init


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("SF.ViewerH Settings")
        self.geometry("800x500")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.mainframe = MainFrame(self)
        self.mainframe.grid(column=0, row=0, padx=10, pady=(0, 10), sticky="nsew")





if __name__ == '__main__':
    init.init()
    app = App()
    app.mainloop()