import tkinter as tk
from tkinter import ttk
from datetime import datetime

class StatusModule:
    def __init__(self, parent):
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        # 현재 상태 라벨
        ttk.Label(self.parent, text="현재 상태:").grid(row=0, column=0, padx=(0,5), pady=5, sticky='nw')

        # 상태를 표시할 읽기 전용 텍스트 필드
        self.status_text = tk.Text(self.parent, height=5, width=50, state='disabled')
        self.status_text.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(self.parent, orient='vertical', command=self.status_text.yview)
        scrollbar.grid(row=1, column=1, sticky='ns')
        self.status_text['yscrollcommand'] = scrollbar.set

        # 그리드 설정을 조정하여 텍스트 필드가 창 크기에 맞춰 확장되도록 함
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(1, weight=1)

    def update_status(self, message: str):
        """
        상태 텍스트 필드를 업데이트 하는 함수
        """
        start_time = datetime.now()
        formatted_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        message = formatted_time + " | " + message
        message = message + "\n"

        self.status_text.config(state='normal')
        self.status_text.insert(tk.END, message)
        self.status_text.see(tk.END)
        self.status_text.config(state='disabled')

    def get_widget(self):
        return self.parent