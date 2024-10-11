import tkinter as tk
from tkinter import ttk
from .datas.constants import (EMBEDDING_MODEL_TYPES, EMBEDDING_MODEL_VERSIONS,
                              SUMMARY_MODEL_TYPES, SUMMARY_MODEL_VERSIONS)
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
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
        
        processed_results = []
        for google_data in crawling_result:
            processed_google_data = await self.process_google_data(google_data, chunk_size, overlap)
            processed_results.append(processed_google_data)
        
        self.status_module.update_status("전처리 완료")
        return processed_results

    async def process_google_data(self, google_data, chunk_size, overlap):
        # 텍스트 청크 분할
        google_data.google_json = self.do_chucking(google_data.google_json, chunk_size, overlap)
        
        # Google 데이터 임베딩 (배치 임베딩 사용)
        google_data.vectorized_json = self.embedding.get_text_embeddings_batch(google_data.google_json)
        
        # Naver 블로그 데이터 임베딩 (비동기 처리)
        tasks = []
        for naver_data in google_data.blog_datas:
            if naver_data.content is not None:
                print(naver_data.link)
                naver_data.content = self.do_chucking(naver_data.content, chunk_size, overlap)
                tasks.append(self.embedding.get_text_embeddings_async(naver_data.content))
            else:
                self.status_module.update_status(f"경고: Naver 데이터 '{google_data.name}'의 내용이 없습니다.")
        
        # 모든 Naver 데이터 임베딩 완료 대기
        naver_results = await asyncio.gather(*tasks, return_exceptions=True)
        for naver_data, vectorized_content in zip(google_data.blog_datas, naver_results):
            if naver_data.content is not None:
                if isinstance(vectorized_content, Exception):
                    self.status_module.update_status(f"경고: Naver 데이터 '{google_data.name}' 임베딩 중 오류 발생: {vectorized_content}")
                else:
                    naver_data.vectorized_content = vectorized_content
        
        self.status_module.update_status(f"Google 데이터 처리 완료: {google_data.name}")
        return google_data
        
    def do_chucking(self, data, size, overlap) -> list:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=int(size), chunk_overlap=int(overlap))
        isDict = isinstance(data, dict)

        if isDict:
            data = json.dumps(data, ensure_ascii=False)

        doc = Document(page_content=data) 
        chunked_list = text_splitter.split_documents([doc])

        if isDict:
            # 청킹된 문서를 dict 리스트로 변환
            return [{"chunk": i, "content": chunk.page_content} for i, chunk in enumerate(chunked_list)]

        return [chunk.page_content for chunk in chunked_list]

    def get_widget(self):
        return self.main_frame