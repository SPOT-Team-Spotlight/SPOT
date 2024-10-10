import sys
from tkinter import ttk, Menu
from modules.settings import SettingsWindow
from creator_api.vdb_creator import VdbCreatorModule
from creator_api.api_key import ApiKey
from creator_api.vdb_retriever import VdbRetrieverModule
from modules.vdb_selector import VdbSelectorModule
from modules.vdb_merge import VdbMergeModule
from configuration import load_config, save_config, update_module_config

class Application:
    def __init__(self, root):   
        self.root = root
        self.root.title("Good DB Mgr (alpha ver1.01)")

        self.config = load_config()
        self.apply_settings(self.config)
        self.create_widgets()

        self.modules = {}   

        self.root.bind("<<SettingsChanged>>", self.on_settings_changed)

    def open_settings(self):
        """
        application의 설정창을 여는 항목
        """
        self.open_module('settings', SettingsWindow)

    def open_vdb_creator(self):
        """
        vdb 생성하는 창을 띄워주는 함수
        """
        self.open_module('vdb_creator', VdbCreatorModule)

    def open_vdb_selector(self):
        """
        vdb 메타 데이터를 출력하는 창을 띄워주는 함수
        """
        self.open_module('vdb_selector', VdbSelectorModule)

    def open_vdb_retriever(self):
        """
        vdb 검색하는 창을 띄워주는 함수
        """
        self.open_module('vdb_retriever', VdbRetrieverModule)

    def open_api_status(self):
        """
        api 상태 관리창을 여는 항목
        """
        self.open_module('api_key', ApiKey)

    def open_vdb_merge(self):
        """
        vdb 병합툴을 여는 항목
        """
        self.open_module('vdb_merge', VdbMergeModule)

    def open_module(self, module_name, ModuleClass):
        if module_name not in self.modules or not self.modules[module_name].window.winfo_exists():
            self.modules[module_name] = ModuleClass(self.root, self.config)
            self.modules[module_name].window.protocol("WM_DELETE_WINDOW", lambda: self.on_module_close(module_name))
        else:
            self.modules[module_name].window.lift()

    def on_module_close(self, module_name):
        if module_name in self.modules:
            self.modules[module_name].on_closing()
            del self.modules[module_name]

    def on_settings_changed(self, event):
        self.apply_settings(self.config)

    def apply_settings(self, new_settings):
        """
        Application의 환경 설정을 할 수 있는 setting 창을 여는 함수
        """
        self.config.update(new_settings)
        self.root.option_add("*Font", f"{self.config['font_family']} {self.config['font_size']}")
        
        if 'theme' in new_settings:
            self.root.set_theme(new_settings['theme'])
        else:
            print(f"테마 설정에 실패하였습니다. 기본 테마(arc)를 사용합니다")
            self.root.set_theme('arc')  # 기본 테마로 'arc' 사용
        
        style = ttk.Style()
        if self.config['button_style'] == 'rounded':
            style.configure('TButton', relief='rounded', padding=6)
        elif self.config['button_style'] == 'flat':
            style.configure('TButton', relief='flat', padding=6)
        
        self.root.update()    

    def create_widgets(self):
        """
        Application의 컨텐츠가 든 함수
        """
        # 메뉴바 생성
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # 설정 메뉴 추가
        settings_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="설정", menu=settings_menu)
        settings_menu.add_command(label="설정 열기", command=self.open_settings)

        # 상태 메뉴 추가
        status_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="상태", menu=status_menu)
        status_menu.add_command(label="api key 관리", command=self.open_api_status)

        # 구분선 추가
        separator = ttk.Separator(self.root, orient='horizontal')
        separator.pack(fill='x')

        self.frame = ttk.Frame(self.root)
        self.frame.pack(expand=True, fill='both')

        self.label_frame = ttk.Frame(self.frame, padding="5")
        self.label_frame.pack(pady=10)
        
        self.label = ttk.Label(self.label_frame, text="SPOT DB Mgr")
        self.label.pack()
        self.label = ttk.Label(self.label_frame, text="for Team Spotlight")
        self.label.pack()

        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(pady=10)

        self.create_button = ttk.Button(self.button_frame, text="생성하기", command=self.open_vdb_creator)
        self.create_button.grid(row=0, column=0, padx=10, pady=10)

        self.select_button = ttk.Button(self.button_frame, text="출력하기", command=self.open_vdb_selector)
        self.select_button.grid(row=0, column=1, padx=10, pady=10)

        self.retrieve_button = ttk.Button(self.button_frame, text="검색하기", command=self.open_vdb_retriever)
        self.retrieve_button.grid(row=0, column=2, padx=10, pady=10)

        self.retrieve_button = ttk.Button(self.button_frame, text="병합하기", command=self.open_vdb_merge)
        self.retrieve_button.grid(row=0, column=3, padx=10, pady=10)
        
        self.exit_button = ttk.Button(self.frame, text="종료", command=self.exit_application)
        self.exit_button.pack(pady=10)

    def exit_application(self):
        # 열려 있는 모든 모듈의 설정 저장
        for module_name, module in list(self.modules.items()):
            if module.window.winfo_exists():
                update_module_config(self.config, module_name, module.window)
                module.window.destroy()

        # 모든 자식 위젯 파괴
        for widget in self.root.winfo_children():
            widget.destroy()

        save_config(self.root, self.config)
        
        # 루트 창에 종료 이벤트 발생
        self.root.event_generate("<<ApplicationExit>>")
        
        # 루트 창 종료
        self.root.quit()
        
    def run(self):
        self.root.geometry(f"{self.config['width']}x{self.config['height']}+{self.config['x']}+{self.config['y']}")
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)
        self.root.mainloop()