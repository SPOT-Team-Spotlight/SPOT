import tkinter as tk
from tkinter import ttk, filedialog
from configuration import save_module_config, load_module_config
from creator_api.faissVectorStore import FaissVectorStore
from creator_api.embeddings import EmbeddingModule
from creator_api.datas.constants import EMBEDDING_MODEL_TYPES, EMBEDDING_MODEL_VERSIONS
import os

class VdbRetrieverModule:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.window = tk.Toplevel(parent)
        self.window.title("VDB Retriever")
        
        # 저장된 설정 적용
        window_config = load_module_config('vdb_retriever')
        self.window.geometry(f"{window_config.get('width', 600)}x{window_config.get('height', 500)}" \
                     f"+{window_config.get('x', 150)}+{window_config.get('y', 150)}")

        self.vector_store = None
        self.embedding = None
        
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.project_root, 'data')
        
        self.create_widgets()
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 파일 선택 섹션
        file_frame = ttk.Frame(self.main_frame)
        file_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(file_frame, text="Index 파일:").pack(side=tk.LEFT, padx=(0, 5))
        self.index_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.index_path_var, width=40).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_frame, text="선택", command=lambda: self.select_file('index')).pack(side=tk.LEFT)

        file_frame2 = ttk.Frame(self.main_frame)
        file_frame2.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(file_frame2, text="Metadata 파일:").pack(side=tk.LEFT, padx=(0, 5))
        self.metadata_path_var = tk.StringVar()
        ttk.Entry(file_frame2, textvariable=self.metadata_path_var, width=40).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_frame2, text="선택", command=lambda: self.select_file('metadata')).pack(side=tk.LEFT)

        self.load_button = ttk.Button(self.main_frame, text="데이터 로드", command=self.load_data)
        self.load_button.pack(pady=(0, 10))

        # 상태 메시지
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.pack(pady=(10, 0))

        # 나머지 위젯들을 생성하지만 초기에는 숨김
        self.create_hidden_widgets()

    def create_hidden_widgets(self):
        # 임베딩 모델 선택
        self.embedding_frame = ttk.Frame(self.main_frame)
        ttk.Label(self.embedding_frame, text="임베딩 모델:").pack(side=tk.LEFT, padx=(0, 5))
        self.embedding_model_type = tk.StringVar(value=EMBEDDING_MODEL_TYPES[0])
        self.embedding_type_entry = ttk.Combobox(self.embedding_frame, textvariable=self.embedding_model_type, 
                                                 values=EMBEDDING_MODEL_TYPES, state="readonly", width=15)
        self.embedding_type_entry.pack(side=tk.LEFT, padx=(0, 5))

        self.embedding_model_version = tk.StringVar(value=EMBEDDING_MODEL_VERSIONS[EMBEDDING_MODEL_TYPES[0]][0])
        self.embedding_version_entry = ttk.Combobox(self.embedding_frame, textvariable=self.embedding_model_version, 
                                                    values=EMBEDDING_MODEL_VERSIONS[EMBEDDING_MODEL_TYPES[0]], 
                                                    state="readonly", width=20)
        self.embedding_version_entry.pack(side=tk.LEFT, padx=(0, 5))

        self.embedding_type_entry.bind("<<ComboboxSelected>>", self.update_version_options)

        # 쿼리 입력 섹션
        self.query_frame = ttk.Frame(self.main_frame)
        self.query_label = ttk.Label(self.query_frame, text="쿼리:")
        self.query_label.pack(side=tk.LEFT, padx=(0, 5))
        self.query_entry = ttk.Entry(self.query_frame)
        self.query_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.search_button = ttk.Button(self.query_frame, text="검색", command=self.search)
        self.search_button.pack(side=tk.LEFT, padx=(5, 0))

        # 결과 개수 조절 섹션
        self.count_frame = ttk.Frame(self.main_frame)
        self.count_label = ttk.Label(self.count_frame, text="결과 개수:")
        self.count_label.pack(side=tk.LEFT, padx=(0, 5))
        self.count_var = tk.StringVar(value="5")
        self.count_entry = ttk.Entry(self.count_frame, textvariable=self.count_var, width=5)
        self.count_entry.pack(side=tk.LEFT)
        self.increase_button = ttk.Button(self.count_frame, text="+", command=self.increase_count, width=2)
        self.increase_button.pack(side=tk.LEFT, padx=(5, 0))
        self.decrease_button = ttk.Button(self.count_frame, text="-", command=self.decrease_count, width=2)
        self.decrease_button.pack(side=tk.LEFT, padx=(5, 0))

        # 결과 표시 섹션
        self.result_frame = ttk.Frame(self.main_frame)
        self.result_label = ttk.Label(self.result_frame, text="결과:")
        self.result_label.pack(anchor=tk.W)
        self.result_text = tk.Text(self.result_frame, wrap=tk.WORD, state="disabled")
        self.result_text.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.configure(yscrollcommand=scrollbar.set)

    def show_hidden_widgets(self):
        self.embedding_frame.pack(fill=tk.X, pady=(0, 10))
        self.query_frame.pack(fill=tk.X, pady=(0, 10))
        self.count_frame.pack(fill=tk.X, pady=(0, 10))
        self.result_frame.pack(fill=tk.BOTH, expand=True)

    def update_version_options(self, event):
        selected_type = self.embedding_model_type.get()
        versions = EMBEDDING_MODEL_VERSIONS.get(selected_type, [])
        self.embedding_version_entry['values'] = versions
        self.embedding_model_version.set(versions[0] if versions else '')

    def select_file(self, file_type):
        if file_type == 'index':
            filetypes = [("Binary files", "*.bin"), ("All files", "*.*")]
            title = "Select Index File"
        elif file_type == 'metadata':
            filetypes = [("Pickle files", "*.pkl"), ("All files", "*.*")]
            title = "Select Metadata File"
        else:
            return

        initial_dir = self.data_dir if os.path.exists(self.data_dir) else self.project_root

        filename = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes,
            initialdir=initial_dir
        )
        if filename:
            if file_type == 'index':
                self.index_path_var.set(filename)
            elif file_type == 'metadata':
                self.metadata_path_var.set(filename)

    def load_data(self):
        index_file = self.index_path_var.get()
        metadata_file = self.metadata_path_var.get()
        if index_file and metadata_file:
            try:
                self.vector_store = FaissVectorStore(index_file=index_file, metadata_file=metadata_file)
                self.vector_store.load_index()
                self.status_var.set("데이터 로드 완료")
                self.show_hidden_widgets()
                self.load_button.config(state="disabled")  # 데이터 로드 후 버튼 비활성화
            except Exception as e:
                self.status_var.set(f"데이터 로드 실패: {str(e)}")
        else:
            self.status_var.set("Index와 Metadata 파일을 모두 선택해주세요.")

    def increase_count(self):
        current = int(self.count_var.get())
        self.count_var.set(str(current + 1))

    def decrease_count(self):
        current = int(self.count_var.get())
        if current > 1:
            self.count_var.set(str(current - 1))

    def search(self):
        query = self.query_entry.get()
        k = int(self.count_var.get())

        embedding_type = self.embedding_model_type.get()
        embedding_version = self.embedding_model_version.get()

        if self.embedding is None:
            self.embedding = EmbeddingModule(model_name=embedding_type, version=embedding_version)

        try:
            query_vector = self.embedding.get_text_embedding_sync(query)
            distances, indices = self.vector_store.search(query_vector, k * 2)
            
            results = []
            seen_data_ids = set()
            
            for distance, idx in zip(distances[0], indices[0]):
                if idx < len(self.vector_store.metadata):
                    metadata = self.vector_store.metadata[idx]
                    data_id = metadata.get('data_id')
                    
                    if data_id not in seen_data_ids:
                        seen_data_ids.add(data_id)
                        
                        result_str = f"Distance: {distance:.4f}\n"
                        for key, value in metadata.items():
                            result_str += f"{key}: {value}\n"
                        
                        results.append(result_str)
                        
                        if len(results) == k:
                            break
                else:
                    break

            if len(results) < k:
                self.status_var.set(f"주의: 요청한 {k}개의 결과 중 {len(results)}개만 찾았습니다.")
            else:
                self.status_var.set("검색 완료")

            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)
            for i, result in enumerate(results, 1):
                self.result_text.insert(tk.END, f"{i}.\n{result}\n\n")
            self.result_text.config(state="disabled")

        except Exception as e:
            self.status_var.set(f"검색 중 오류 발생: {str(e)}")

    def on_closing(self):
        window_config = {
            'width': self.window.winfo_width(),
            'height': self.window.winfo_height(),
            'x': self.window.winfo_x(),
            'y': self.window.winfo_y()
        }
        save_module_config('vdb_retriever', window_config)
        self.window.destroy()