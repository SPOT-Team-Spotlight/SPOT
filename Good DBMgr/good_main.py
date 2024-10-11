"""
웹 크롤링을 통해서 Faiss DB를 만드는 프로그램 
"""
import tkinter as tk
from ttkthemes import ThemedTk
from application import Application

class MainApplication:
    def __init__(self):
        self.root = ThemedTk(theme="arc")  
        self.icon = tk.PhotoImage(file="logo.png")
        self.root.wm_iconphoto(True, self.icon)
        self.app = Application(self.root)

    def run(self):
        self.app.run()

    def cleanup(self):
        # 이미지 객체 삭제
        del self.icon
        # 루트 창 업데이트 및 파괴
        self.root.update()
        self.root.destroy()

if __name__ == "__main__":
    main_app = MainApplication()
    try:
        main_app.run()
    finally:
        main_app.cleanup()