import tkinter as tk
from tkinter import ttk
from .naver_service import NaverService
from .datas.constants import TEST_MODE, GATHER_MODE
from configuration import load_module_config, save_module_config

class CrawlingModule:
    def __init__(self, parent, status_module, config=None):
        self.parent = parent
        self.status_module = status_module
        self.config = config or {}
        self.crawling_mode = tk.StringVar(value=self.config.get('mode', TEST_MODE))
        self.recent_regions = self.config.get('recent_regions', [])
        self.recent_keywords = self.config.get('recent_keywords', [])
        self.crawling_tool = NaverService()
        self.create_widgets()
    
    def create_widgets(self):
        self.main_frame = ttk.Frame(self.parent, padding="10")
        
        # 지역 라벨과 입력 필드
        ttk.Label(self.main_frame, text="지역:").grid(row=0, column=0, padx=(0,5), pady=5, sticky='e')
        self.region_entry = ttk.Entry(self.main_frame, width=15)
        self.region_entry.grid(row=0, column=1, padx=(0,15), pady=5, sticky='w')
        self.region_entry.insert(0, self.config.get('region', ''))
        self.region_entry.bind("<FocusIn>", lambda e: self.show_recent_items(e, "region"))

        # 키워드 라벨과 입력 필드
        ttk.Label(self.main_frame, text="키워드:").grid(row=0, column=2, padx=(0,5), pady=5, sticky='e')
        self.keyword_entry = ttk.Entry(self.main_frame, width=15)
        self.keyword_entry.grid(row=0, column=3, padx=(0,5), pady=5, sticky='w')
        self.keyword_entry.insert(0, self.config.get('keyword', ''))
        self.keyword_entry.bind("<FocusIn>", lambda e: self.show_recent_items(e, "keyword"))

        # 크롤링 모드 라벨
        ttk.Label(self.main_frame, text="크롤링 모드:").grid(row=2, column=0, padx=(0,5), pady=5, sticky='w')

        # 테스트 모드 라디오 버튼
        ttk.Radiobutton(self.main_frame, text=TEST_MODE, 
                        variable=self.crawling_mode, value=TEST_MODE).grid(row=2, column=1, padx=(0,5), pady=5, sticky='w')

        # 데이터 수집 모드 라디오 버튼
        ttk.Radiobutton(self.main_frame, text=GATHER_MODE, 
                        variable=self.crawling_mode, value=GATHER_MODE).grid(row=2, column=2, padx=(0,5), pady=5, sticky='w')

    def load_config(self):
        crawling_config = load_module_config('crawling')
        self.region = crawling_config.get('region', '')
        self.keyword = crawling_config.get('keyword', '')
        self.mode = crawling_config.get('mode', TEST_MODE)
        self.recent_regions = crawling_config.get('recent_regions', [])
        self.recent_keywords = crawling_config.get('recent_keywords', [])

    def get_config(self):
        return {
            'region': self.region_entry.get(),
            'keyword': self.keyword_entry.get(),
            'mode': self.crawling_mode.get(),
            'recent_regions': self.recent_regions,
            'recent_keywords': self.recent_keywords
        }

    def show_recent_items(self, event, field_type):
        if field_type == "region":
            items = self.recent_regions
            entry = self.region_entry
        else:
            items = self.recent_keywords
            entry = self.keyword_entry

        if not items:
            return

        popup = tk.Menu(self.main_frame, tearoff=0)
        for item in items:
            popup.add_command(label=item, command=lambda i=item: self.set_entry(entry, i))

        try:
            popup.tk_popup(self.main_frame.winfo_rootx() + entry.winfo_x(), 
                           self.main_frame.winfo_rooty() + entry.winfo_y() + entry.winfo_height())
        finally:
            popup.grab_release()

    def set_entry(self, entry, value):
        entry.delete(0, tk.END)
        entry.insert(0, value)

    def update_recent_items(self, field_type, value):
        if field_type == "region":
            items = self.recent_regions
        else:
            items = self.recent_keywords

        if value in items:
            items.remove(value)
        items.insert(0, value)
        items = items[:5]  # 최근 5개의 항목만 유지함

        if field_type == "region":
            self.recent_regions = items
        else:
            self.recent_keywords = items

    async def start_crawling(self, keyword: str, region: str, mode: str):
        """
        크롤링을 시작하는 함수
        """
        self.status_module.update_status(f"키워드: {keyword}, 지역: {region}, 모드: {mode}(으)로 크롤링을 시작합니다")
        
        # 크롤링 시작 전에 현재 설정 저장 및 최근 항목 업데이트
        self.update_recent_items("region", region)
        self.update_recent_items("keyword", keyword)
        
        try:
            # 모드에 따라 display 값 설정
            display = 10 if mode == TEST_MODE else 100         

            results = self.crawling_tool.crawling_naver_blog_data(query=keyword, region=region, display=display)

            total_results = len(results)
            
            for i, result in enumerate(results):
                status_message = f"처리 중: {result.name} ({i+1}/{total_results})"
                self.status_module.update_status(status_message)

            self.status_module.update_status("크롤링이 완료되었습니다.")
            return results
        except Exception as e:
            error_message = f"크롤링 중 오류 발생: {str(e)}"
            self.status_module.update_status(error_message)
            return None

    def get_widget(self):
        return self.main_frame