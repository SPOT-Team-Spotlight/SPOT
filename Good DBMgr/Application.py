from tkinter import ttk
from settings import SettingsWindow
from configuration import load_config, save_config
from modules.crawling import start_crawling

class Application:
    def __init__(self, root):
        self.root = root
        self.root.title("Good DB Mgr for <Team SPOTLIGHT>")

        self.config = load_config()
        self.apply_settings(self.config)

        self.create_widgets()

    def open_settings(self):
        """
        application의 설정을 불러오는 항목
        """
        SettingsWindow(self.root, self.config, self.apply_settings) 

    def apply_settings(self, new_settings):
        self.config.update(new_settings)
        self.root.option_add("*Font", f"{self.config['font_family']} {self.config['font_size']}")
        
        style = ttk.Style()
        if self.config['theme'] == 'dark':
            style.theme_use('clam')
            style.configure(".", background="gray20", foreground="white")
        else:
            style.theme_use('default')
        
        if self.config['button_style'] == 'rounded':
            style.configure('TButton', relief='rounded', padding=6)
        elif self.config['button_style'] == 'flat':
            style.configure('TButton', relief='flat', padding=6)
        
        self.root.update()    

    def create_widgets(self):
        self.frame = ttk.Frame(self.root)
        self.frame.pack(expand=True, fill='both')

        self.label = ttk.Label(self.frame, text="Press the button")
        self.label.pack(pady=20)

        self.button = ttk.Button(self.frame, text="크롤링 시작하기", command=start_crawling("강남구","맛집"))
        self.button.pack(expand=True)

        self.settings_button = ttk.Button(self.frame, text="설정", command=self.open_settings)
        self.settings_button.pack(pady=10)

    def run(self):
        self.root.geometry(f"{self.config['width']}x{self.config['height']}+{self.config['x']}+{self.config['y']}")
        self.root.protocol("WM_DELETE_WINDOW", lambda: (save_config(self.root, self.config), self.root.destroy()))
        self.root.mainloop()