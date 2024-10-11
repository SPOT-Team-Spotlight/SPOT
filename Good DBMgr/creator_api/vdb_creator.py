import asyncio
import threading
import tkinter as tk
from tkinter import ttk
from creator_api.crawling import CrawlingModule
from creator_api.preprocessing import PreprocessingModule
from creator_api.vdb_save import VdbSaveModule
from configuration import load_module_config, save_module_config
from .status_module import StatusModule
from .datas.constants import TEST_MODE, GATHER_MODE

class VdbCreatorModule:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.window = tk.Toplevel(parent)
        self.window.title("VDB Creator")
        
        # 저장된 설정 적용
        self.window_config = load_module_config('vdb_creator')
        self.window.geometry(f"{self.window_config.get('width', 600)}x{self.window_config.get('height', 500)}" \
                     f"+{self.window_config.get('x', 150)}+{self.window_config.get('y', 150)}")

        self.crawling_results = None
        self.create_widgets()

        # 창 닫힐 때 설정 저장
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        # asyncio 이벤트 루프 생성
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.thread = threading.Thread(target=self.run_async_loop, daemon=True)
        self.thread.start()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # grid 설정
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=0)

        # 상단 프레임
        top_frame = ttk.Frame(self.main_frame)
        top_frame.grid(row=0, column=0, pady=10, sticky='nw')

        # 라벨
        self.label = ttk.Label(top_frame, text="VDB Creator")
        self.label.pack(side=tk.LEFT, padx=(0, 10))

        # VDB 생성 버튼
        self.create_vdb_button = ttk.Button(top_frame, text="VDB 생성하기", command=self.start_vdb_creation)
        self.create_vdb_button.pack(side=tk.LEFT)

        # PanedWindow 생성
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.VERTICAL)
        self.paned_window.grid(row=1, column=0, sticky='nsew')

        # 탭 컨트롤 생성
        self.tab_control = ttk.Notebook(self.paned_window)
        self.paned_window.add(self.tab_control, weight=3)
        
        # 상태 모듈 추가
        status_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(status_frame, weight=1)
        self.status_module = StatusModule(status_frame)

        # 크롤링 탭
        crawling_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(crawling_tab, text='크롤링')
        
        # 크롤링 모듈의 위젯 추가
        crawling_config = self.window_config.get('crawling', {})
        self.crawling_module = CrawlingModule(crawling_tab, self.status_module, crawling_config)
        crawling_widget = self.crawling_module.get_widget()
        crawling_widget.pack(fill=tk.BOTH, expand=True)

        # 데이터 처리 탭
        data_processing_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(data_processing_tab, text='데이터 전처리')

        # 전처리 모듈의 위젯 추가 
        preprocessing_config = self.window_config.get('preprocessing', {})
        self.preprocessing_module = PreprocessingModule(data_processing_tab, self.status_module, preprocessing_config)
        processing_widget = self.preprocessing_module.get_widget()
        processing_widget.pack(fill=tk.BOTH, expand=True)

        # VDB 저장 탭
        vdb_save_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(vdb_save_tab, text='VDB 저장')

        # VdbSaveModule 인스턴스 생성 및 위젯 추가
        self.vdb_save_module = VdbSaveModule(vdb_save_tab, self.status_module)
        vdb_save_widget = self.vdb_save_module.get_widget()
        vdb_save_widget.pack(fill=tk.BOTH, expand=True)

        # 종료 버튼 추가
        self.close_button = ttk.Button(self.main_frame, text="Close", command=self.on_closing)
        self.close_button.grid(row=3, column=0, pady=10, sticky='se')

    def start_vdb_creation(self):
        self.window.after(0, lambda: self.create_vdb_button.config(state='disabled'))
        asyncio.run_coroutine_threadsafe(self.async_vdb_creation(), self.loop)

    def run_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def async_vdb_creation(self):
        try:
            self.status_module.update_status("VDB 생성 프로세스 시작...")

            # 크롤링 시작
            self.status_module.update_status("크롤링 시작...")
            keyword = self.crawling_module.keyword_entry.get()
            region = self.crawling_module.region_entry.get()
            mode = self.crawling_module.crawling_mode.get()

            if len(keyword) > 1 and len(region) > 1:
                self.crawling_results = await self.crawling_module.start_crawling(keyword, region, mode)
                if not self.crawling_results:
                    raise Exception("크롤링 결과가 없습니다.")
            else:
                raise Exception("검색어 또는 지역이 누락되었습니다.")

            # 전처리 시작
            self.status_module.update_status("데이터 전처리 시작...")
            processed_results = await self.preprocessing_module.start_preprocessing(self.crawling_results)
            if not processed_results:
                raise Exception("전처리 결과가 없습니다.")

            # VDB 저장
            self.status_module.update_status("VDB 저장 시작...")
            self.vdb_save_module.set_preprocessed_data(processed_results)
            success = await self.vdb_save_module.save_to_vdb()
            if not success:
                raise Exception("VDB 저장에 실패했습니다.")

            self.status_module.update_status("VDB 생성 프로세스 완료")

        except Exception as e:
            self.status_module.update_status(f"오류 발생: {str(e)}")
        finally:
            self.window.after(0, lambda: self.create_vdb_button.config(state='normal'))

    def on_closing(self):
        # 현재 설정 저장
        self.window_config.update({
            'width': self.window.winfo_width(),
            'height': self.window.winfo_height(),
            'x': self.window.winfo_x(),
            'y': self.window.winfo_y(),
            'crawling': self.crawling_module.get_config(),
            'preprocessing': self.preprocessing_module.get_config()
        })
        save_module_config('vdb_creator', self.window_config)
        self.window.destroy()

    def run(self):
        self.window.mainloop()