import os
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from dotenv import dotenv_values
from configuration import save_module_config, load_module_config 

env_path = Path('.') / '.env'

if env_path.exists():
    env_const = dotenv_values(env_path)
else:
    print(".env 파일을 찾지 못했습니다.")
    env_const = {}

def get_key(keyName) -> str:
    """
    키를 요청 받으면 있으면 반환, 없으면 None을 하는 함수
    """
    return env_const.get(keyName, None)
    
class ApiKey():
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.window = tk.Toplevel(parent)
        self.window.title("API키 관리")
        self.window.resizable(False, False)

         # 저장된 설정 적용
        window_config = load_module_config('api_key') 
        self.window.geometry(f"{window_config.get('width', 500)}x{window_config.get('height', 400)}" \
                     f"+{window_config.get('x', 300)}+{window_config.get('y', 300)}")

        # 메인 프레임 생성
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill='both', expand=True)

        # 왼쪽 프레임 (스크롤 영역)
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side='left', fill='both', expand=True)

        # 스크롤바와 캔버스 생성
        self.canvas = tk.Canvas(self.left_frame)
        self.scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 오른쪽 프레임 (버튼 영역)
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side='right', fill='y', padx=10)

        self.create_widgets()

        # 캔버스와 스크롤바 배치
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 창 크기를 위젯에 맞게 조절하고 최대 높이 설정
        self.window.update()
        window_width = min(self.window.winfo_reqwidth(), 500)  # 최대 너비를 500px로 제한
        window_height = min(self.window.winfo_reqheight(), 400)  # 최대 높이를 400px로 제한
        self.window.geometry(f"{window_width}x{window_height}")

        # 캔버스 크기 설정
        self.canvas.config(width=window_width-100, height=window_height)  # 오른쪽 버튼 영역을 위해 너비 조정

        # 창 닫힐 때 설정 저장
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def check_status(self) -> dict:
        status = {key: bool(value) for key, value in env_const.items()}
        return status

    def create_widgets(self):
        """
        내부 항목을 추가하는 항목
        """
        # 제목 라벨 추가
        title_label = ttk.Label(self.scrollable_frame, text="사용중인 API키", font=("Helvetica", 12, "bold"))
        title_label.pack(pady=(10, 5))

        status = self.check_status()

        for name, value in status.items():
            frame = ttk.Frame(self.scrollable_frame)
            frame.pack(fill='x', padx=5, pady=2)

            label = ttk.Label(frame, text=f"{name}:")
            label.pack(side='left', padx=(0, 10))

            var = tk.BooleanVar(value=value)
            checkbox = ttk.Checkbutton(frame, variable=var, state='disabled')
            checkbox.pack(side='left')

            # 시각적 피드백을 위한 추가 레이블
            status_label = ttk.Label(frame, text="Active" if value else "Inactive",
                                     foreground="green" if value else "red")
            status_label.pack(side='left', padx=(10, 0))

        # 설명 라벨 추가
        description_label = ttk.Label(self.scrollable_frame, text="Active는 키의 유무만 파악할 뿐 해당 키 값이 유효한지 알 수 없습니다", 
                                    wraplength=300, justify="center")
        description_label.pack(pady=(10, 10))

        # "키 추가" 버튼 추가 (오른쪽 프레임에)
        add_key_button = ttk.Button(self.right_frame, text="키 추가", command=self.add_key)
        add_key_button.pack(side='top', pady=10)

    def add_key(self):
        # 여기에 키 추가 로직을 구현합니다.
        print("키 추가 버튼이 클릭되었습니다.")
        # 예: 새 창을 열어 키 입력 받기, 파일에 저장하기 등

    def on_closing(self):
        window_config = {
            'width': self.window.winfo_width(),
            'height': self.window.winfo_height(),
            'x': self.window.winfo_x(),
            'y': self.window.winfo_y()
        }
        save_module_config('api_key', window_config)  # 변경된 부분
        self.window.destroy()
