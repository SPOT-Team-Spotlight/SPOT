import tkinter as tk
from tkinter import ttk
from .datas.constants import (EMBEDDING_MODEL_TYPES, EMBEDDING_MODEL_VERSIONS,
                              SUMMARY_MODEL_TYPES, SUMMARY_MODEL_VERSIONS)
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .embeddings import EmbeddingModule
import asyncio

class PreprocessingModule:
    def __init__(self, parent, status_module, config=None):
        self.parent = parent
        self.status_module = status_module
        self.config = config or {}
        self.embedding = None
        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.parent, padding="10")
        
        # 임베딩 모델 선택
        ttk.Label(self.main_frame, text="임베딩 모델:").grid(row=0, column=0, padx=(0,5), pady=5, sticky='e')
        self.embedding_model_type = tk.StringVar()
        self.embedding_type_dropdown = ttk.Combobox(self.main_frame, textvariable=self.embedding_model_type, 
                                                    values=EMBEDDING_MODEL_TYPES, state="readonly", width=15)
        self.embedding_type_dropdown.grid(row=0, column=1, padx=(0,5), pady=5, sticky='w')
        self.embedding_type_dropdown.set(EMBEDDING_MODEL_TYPES[0])
        self.embedding_type_dropdown.bind("<<ComboboxSelected>>", self.update_embedding_versions)

        self.embedding_model_version = tk.StringVar()
        self.embedding_version_dropdown = ttk.Combobox(self.main_frame, textvariable=self.embedding_model_version, 
                                                       state="readonly", width=20)
        self.embedding_version_dropdown.grid(row=0, column=2, padx=(0,15), pady=5, sticky='w')
        self.update_embedding_versions()

        # 요약 모델 선택 (미지원)
        ttk.Label(self.main_frame, text="요약 모델 (미지원):").grid(row=1, column=0, padx=(0,5), pady=5, sticky='e')
        self.summary_model_type = tk.StringVar()
        self.summary_type_dropdown = ttk.Combobox(self.main_frame, textvariable=self.summary_model_type, 
                                                  values=SUMMARY_MODEL_TYPES, state="disabled", width=15)
        self.summary_type_dropdown.grid(row=1, column=1, padx=(0,5), pady=5, sticky='w')
        self.summary_type_dropdown.set(SUMMARY_MODEL_TYPES[0])

        self.summary_model_version = tk.StringVar()
        self.summary_version_dropdown = ttk.Combobox(self.main_frame, textvariable=self.summary_model_version, 
                                                     state="disabled", width=20)
        self.summary_version_dropdown.grid(row=1, column=2, padx=(0,15), pady=5, sticky='w')
        self.update_summary_versions()

        # 청킹 사이즈 입력
        ttk.Label(self.main_frame, text="청킹 사이즈:").grid(row=2, column=0, padx=(0,5), pady=5, sticky='e')
        self.chunk_size = tk.StringVar(value="200")
        self.chunk_size_entry = ttk.Entry(self.main_frame, textvariable=self.chunk_size, width=10)
        self.chunk_size_entry.grid(row=2, column=1, padx=(0,15), pady=5, sticky='w')

        # 오버랩 입력
        ttk.Label(self.main_frame, text="오버랩:").grid(row=3, column=0, padx=(0,5), pady=5, sticky='e')
        self.overlap = tk.StringVar(value="100")
        self.overlap_entry = ttk.Entry(self.main_frame, textvariable=self.overlap, width=10)
        self.overlap_entry.grid(row=3, column=1, padx=(0,15), pady=5, sticky='w')

    def load_config(self):
        self.embedding_model_type.set(self.config.get('embedding_model_type', EMBEDDING_MODEL_TYPES[0]))
        self.update_embedding_versions()
        self.embedding_model_version.set(
            self.config.get('embedding_model_version', self.embedding_version_dropdown['values'][0] 
                            if self.embedding_version_dropdown['values'] else ''))
        self.chunk_size.set(self.config.get('chunk_size', "200"))
        self.overlap.set(self.config.get('overlap', "100"))

    def get_config(self):
        return {
            'embedding_model_type': self.embedding_model_type.get(),
            'embedding_model_version': self.embedding_model_version.get(),
            'chunk_size': self.chunk_size.get(),
            'overlap': self.overlap.get()
        }

    def update_embedding_versions(self, event=None):
        selected_type = self.embedding_model_type.get()
        versions = EMBEDDING_MODEL_VERSIONS.get(selected_type, [])
        self.embedding_version_dropdown['values'] = versions
        if versions:
            self.embedding_version_dropdown.set(versions[0])
        else:
            self.embedding_version_dropdown.set('')

    def update_summary_versions(self, event=None):
        selected_type = self.summary_model_type.get()
        versions = SUMMARY_MODEL_VERSIONS.get(selected_type, [])
        self.summary_version_dropdown['values'] = versions
        if versions:
            self.summary_version_dropdown.set(versions[0])
        else:
            self.summary_version_dropdown.set('')

    async def start_preprocessing(self, crawling_result):
        embedding_type = self.embedding_model_type.get()
        embedding_version = self.embedding_model_version.get()
        chunk_size = int(self.chunk_size.get())
        overlap = int(self.overlap.get())

        self.status_module.update_status("전처리 시작")

        self.embedding = EmbeddingModule(model_name=embedding_type, version=embedding_version)
        
        processed_results = await self.process_naver_data_list(crawling_result, chunk_size, overlap)
        
        self.status_module.update_status("전처리 완료")
        return processed_results

    async def process_naver_data_list(self, naver_data_list, chunk_size, overlap):
        tasks = []
        for naver_data in naver_data_list:
            if naver_data.content is not None:
                naver_data.content = self.do_chucking(naver_data.content, chunk_size, overlap)
                tasks.append(self.process_single_naver_data(naver_data))
            else:
                self.status_module.update_status(f"경고: Naver 데이터 '{naver_data.name}'의 내용이 없습니다.")
        
        processed_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [result for result in processed_results if not isinstance(result, Exception)]
    
    async def process_single_naver_data(self, naver_data):
        try:
            naver_data.vectorized_content = await self.embedding.get_text_embeddings_async(naver_data.content)
            self.status_module.update_status(f"Naver 데이터 처리 완료: {naver_data.name}")
            return naver_data
        except Exception as e:
            self.status_module.update_status(f"경고: Naver 데이터 '{naver_data.name}' 처리 중 오류 발생: {e}")
            return e
        
    def do_chucking(self, data, size, overlap) -> list:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=int(size), chunk_overlap=int(overlap))
        doc = Document(page_content=data) 
        chunked_list = text_splitter.split_documents([doc])
        return [chunk.page_content for chunk in chunked_list]

    def get_widget(self):
        return self.main_frame