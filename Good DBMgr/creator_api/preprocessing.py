import tkinter as tk
from tkinter import ttk
from .datas.constants import (EMBEDDING_MODEL_TYPES, EMBEDDING_MODEL_VERSIONS,
                              VECTOR_DBS, SUMMARY_MODEL_TYPES, SUMMARY_MODEL_VERSIONS)
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
from .embeddings import EmbeddingModule
import asyncio
from concurrent.futures import ThreadPoolExecutor

class PreprocessingModule:
    def __init__(self, parent, status_module, on_complete_callback):
        self.parent = parent
        self.status_module = status_module
        self.on_complete_callback = on_complete_callback
        self.create_widgets()

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

        # VectorDB 선택
        ttk.Label(self.main_frame, text="Vector DB:").grid(row=1, column=0, padx=(0,5), pady=5, sticky='e')
        self.vector_db = tk.StringVar()
        self.vector_db_dropdown = ttk.Combobox(self.main_frame, textvariable=self.vector_db, 
                                               values=VECTOR_DBS, state="readonly", width=30)
        self.vector_db_dropdown.grid(row=1, column=1, columnspan=2, padx=(0,15), pady=5, sticky='w')
        self.vector_db_dropdown.set(VECTOR_DBS[0])

        # 요약 모델 선택
        ttk.Label(self.main_frame, text="요약 모델:").grid(row=2, column=0, padx=(0,5), pady=5, sticky='e')
        self.summary_model_type = tk.StringVar()
        self.summary_type_dropdown = ttk.Combobox(self.main_frame, textvariable=self.summary_model_type, 
                                                  values=SUMMARY_MODEL_TYPES, state="readonly", width=15)
        self.summary_type_dropdown.grid(row=2, column=1, padx=(0,5), pady=5, sticky='w')
        self.summary_type_dropdown.set(SUMMARY_MODEL_TYPES[0])
        self.summary_type_dropdown.bind("<<ComboboxSelected>>", self.update_summary_versions)

        self.summary_model_version = tk.StringVar()
        self.summary_version_dropdown = ttk.Combobox(self.main_frame, textvariable=self.summary_model_version, 
                                                     state="readonly", width=20)
        self.summary_version_dropdown.grid(row=2, column=2, padx=(0,15), pady=5, sticky='w')
        self.update_summary_versions()

        # 청킹 사이즈 입력
        ttk.Label(self.main_frame, text="청킹 사이즈:").grid(row=3, column=0, padx=(0,5), pady=5, sticky='e')
        self.chunk_size = tk.StringVar(value="200")
        self.chunk_size_entry = ttk.Entry(self.main_frame, textvariable=self.chunk_size, width=10)
        self.chunk_size_entry.grid(row=3, column=1, padx=(0,15), pady=5, sticky='w')

        # 오버랩 입력
        ttk.Label(self.main_frame, text="오버랩:").grid(row=4, column=0, padx=(0,5), pady=5, sticky='e')
        self.overlap = tk.StringVar(value="100")
        self.overlap_entry = ttk.Entry(self.main_frame, textvariable=self.overlap, width=10)
        self.overlap_entry.grid(row=4, column=1, padx=(0,15), pady=5, sticky='w')

    def update_embedding_versions(self, event=None):
        """
        선택된 임베딩 모델에 따라 임베딩 버전을 바꿔주는 함수
        """
        selected_type = self.embedding_model_type.get()
        versions = EMBEDDING_MODEL_VERSIONS.get(selected_type, [])
        self.embedding_version_dropdown['values'] = versions
        if versions:
            self.embedding_version_dropdown.set(versions[0])
        else:
            self.embedding_version_dropdown.set('')

    def update_summary_versions(self, event=None):
        """
        선택된 요약 모델에 따라 요약 모델 버전을 바꿔주는 함수
        """
        selected_type = self.summary_model_type.get()
        versions = SUMMARY_MODEL_VERSIONS.get(selected_type, [])
        self.summary_version_dropdown['values'] = versions
        if versions:
            self.summary_version_dropdown.set(versions[0])
        else:
            self.summary_version_dropdown.set('')

    async def start_preprocessing(self, crawling_result):
        """
        비동기 처리
        """
        embedding_type = self.embedding_model_type.get()
        embedding_version = self.embedding_model_version.get()
        chunk_size = int(self.chunk_size.get())
        overlap = int(self.overlap.get())

        self.status_module.update_status("전처리 시작")

        embedding = EmbeddingModule(model_name=embedding_type, version=embedding_version)
        
        tasks = []
        for google_data in crawling_result:
            tasks.append(self.process_google_data(google_data, embedding, chunk_size, overlap))
        
        await asyncio.gather(*tasks)
        
        self.status_module.update_status("전처리 완료")

        # 전처리 완료 후 콜백 함수 호출
        if self.on_complete_callback:
            self.on_complete_callback(crawling_result)

    async def process_google_data(self, google_data, embedding, chunk_size, overlap):
        google_data.google_json = self.do_chucking(google_data.google_json, chunk_size, overlap)
        
        with ThreadPoolExecutor() as executor:
            google_data.google_json = await asyncio.get_event_loop().run_in_executor(
                executor,
                lambda: [embedding.get_text_embedding(chunk) for chunk in google_data.google_json]
            )
        
        for naver_data in google_data.blog_datas:
            naver_data.content = self.do_chucking(naver_data.content, chunk_size, overlap)
            with ThreadPoolExecutor() as executor:
                naver_data.content = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: [embedding.get_text_embedding(chunk) for chunk in naver_data.content]
                )

        self.status_module.update_status(f"Google 데이터 처리 완료: {google_data.name}")
        
    def do_chucking(self, data, size, overlap) -> list:
        """
        청킹 함수
        """
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=int(size), chunk_overlap=int(overlap))
        isDict = isinstance(data, dict)

        if isDict:
            data = json.dumps(data, ensure_ascii=False)

        doc=Document(page_content=data) 
        chunked_list = text_splitter.split_documents([doc])

        if isDict:
            # 청킹된 문서를 dict 리스트로 변환
            return [{"chunk": i, "content": chunk.page_content} for i, chunk in enumerate(chunked_list)]

        return [chunk.page_content for chunk in chunked_list]

    def get_widget(self):
        return self.main_frame