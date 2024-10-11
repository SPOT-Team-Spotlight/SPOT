import os
import json
import faiss
import pickle
import numpy as np
import tkinter as tk
from tkinter import ttk
from .datas.constants import VECTOR_DBS
from .faissVectorStore import FaissVectorStore

class VdbSaveModule:
    def __init__(self, parent, status_module):
        self.parent = parent
        self.status_module = status_module
        self.preprocessed_data = None
        self.last_id = 0
        self.id_file_path = "./Good DBMgr/vdb_data/last_id.json"
        self.create_widgets()

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # VDB 타입 선택
        vdb_type_frame = ttk.Frame(self.main_frame)
        vdb_type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(vdb_type_frame, text="VDB 타입:").pack(side=tk.LEFT, padx=(0, 5))
        self.vdb_type = tk.StringVar(value=VECTOR_DBS[0])
        self.vdb_type_dropdown = ttk.Combobox(vdb_type_frame, textvariable=self.vdb_type, 
                                              values=VECTOR_DBS, state="readonly", width=15)
        self.vdb_type_dropdown.pack(side=tk.LEFT)

        # 저장 경로 입력
        save_path_frame = ttk.Frame(self.main_frame)
        save_path_frame.pack(fill=tk.X, pady=5)
        ttk.Label(save_path_frame, text="저장 경로:").pack(side=tk.LEFT, padx=(0, 5))
        self.save_path = tk.StringVar(value="./vdb_data")
        self.save_path_entry = ttk.Entry(save_path_frame, textvariable=self.save_path, width=30)
        self.save_path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

    def set_preprocessed_data(self, data):
        self.preprocessed_data = data
        self.status_module.update_status("전처리된 데이터 수신 완료")

    def load_last_id(self):
        if os.path.exists(self.id_file_path):
            with open(self.id_file_path, 'r') as f:
                data = json.load(f)
                self.last_id = data.get('last_id', 0)
        else:
            self.last_id = 0

    def save_last_id(self):
        """
        vdb 데이터 아이디를 불러오는 함수
        """
        with open(self.id_file_path, 'w') as f:
            json.dump({'last_id': self.last_id}, f)

    def get_next_id(self):
        self.last_id += 1
        return self.last_id

    async def save_to_vdb(self):
        """
        vdb에 저장하는 파일
        """
        if self.preprocessed_data is None:
            self.status_module.update_status("저장할 데이터가 없습니다.")
            return False

        vdb_type = self.vdb_type.get()
        save_path = self.save_path.get()

        self.status_module.update_status(f"{vdb_type} VDB에 데이터 저장 시작...")

        # 저장 경로가 존재하지 않으면 생성
        os.makedirs(save_path, exist_ok=True)

        # 마지막 ID 로드
        self.load_last_id()

        if vdb_type == "Faiss":
            success = await self.save_to_faiss(save_path)
        else:
            self.status_module.update_status(f"{vdb_type} VDB 저장은 아직 구현되지 않았습니다.")
            return False

        # 마지막 ID 저장
        self.save_last_id()

        if success:
            self.status_module.update_status(f"{vdb_type} VDB 저장 완료")
        else:
            self.status_module.update_status(f"{vdb_type} VDB 저장 실패")

        return success

    async def save_to_faiss(self, save_path):
        """
        faiss Vector DB에 저장하는 코드
        """
        try:
            vector_store = FaissVectorStore(
                index_file=os.path.join(save_path, "spot_index.bin"),
                metadata_file=os.path.join(save_path, "spot_metadata.pkl")
            )

            for data in self.preprocessed_data:
                data_id = self.get_next_id()
                base_meta = {
                    "data_id": data_id,
                    "name": data.name,
                    "address": data.address
                }
                
                # Google 데이터 처리
                for i, google_item in enumerate(data.vectorized_json):
                    vector_store.add_to_index(
                        {f"google_{data_id}_{i}": google_item},
                        {**base_meta, "content_type": "google", "content_index": i}
                    )

                # Naver 블로그 데이터 처리
                for blog_index, blog_data in enumerate(data.blog_datas):
                    blog_meta = {
                        **base_meta,
                        "content_type": "naver_blog",
                        "blog_index": blog_index,
                        "link": blog_data.link
                    }
                    
                    if isinstance(blog_data.content, list):
                        for chunk_index, (chunk_vector, chunk_content) in enumerate(zip(blog_data.vectorized_content, blog_data.content)):
                            chunk_meta = {
                                **blog_meta,
                                "chunk_index": chunk_index,
                                "chunk_content": chunk_content  # 각 청크의 원본 내용
                            }
                            vector_store.add_to_index(
                                {f"naver_{data_id}_{blog_index}_{chunk_index}": chunk_vector},
                                chunk_meta
                            )
                    else:
                        self.status_module.update_status(f"경고: 블로그 데이터 '{blog_data.title}'의 내용이 리스트 형식이 아닙니다.")

            # 변경사항 저장
            vector_store.save_index()
            
            self.status_module.update_status("Faiss VDB에 데이터 저장 완료")
            return True

        except Exception as e:
            self.status_module.update_status(f"Faiss VDB 저장 중 오류 발생: {str(e)}")
            return False

    def get_widget(self):
        return self.main_frame