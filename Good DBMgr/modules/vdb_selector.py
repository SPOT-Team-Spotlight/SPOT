import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import pickle
import json
import csv
import faiss

class VdbSelectorModule:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.window = tk.Toplevel(parent)
        self.window.title("VDB 출력하기")
        
        # 저장된 설정 적용
        window_config = config.get('vdb_selector', {})
        self.window.geometry(f"{window_config.get('width', 600)}x{window_config.get('height', 500)}" \
                     f"+{window_config.get('x', 150)}+{window_config.get('y', 150)}")
        
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.project_root, '')

        self.index_path = tk.StringVar()
        self.meta_path = tk.StringVar()

        self.create_widgets()

        # 창 닫힐 때 설정 저장
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # "VDB 출력하기" 라벨
        self.title_label = ttk.Label(self.main_frame, text="VDB 출력하기", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Index 파일 선택
        index_frame = ttk.Frame(self.main_frame)
        index_frame.pack(fill=tk.X, pady=5)
        ttk.Label(index_frame, text="Index 파일:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(index_frame, textvariable=self.index_path, width=40).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(index_frame, text="Browse", command=lambda: self.browse_file('index')).pack(side=tk.LEFT, padx=(5, 0))

        # Metadata 파일 선택
        meta_frame = ttk.Frame(self.main_frame)
        meta_frame.pack(fill=tk.X, pady=5)
        ttk.Label(meta_frame, text="Metadata 파일:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(meta_frame, textvariable=self.meta_path, width=40).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(meta_frame, text="Browse", command=lambda: self.browse_file('meta')).pack(side=tk.LEFT, padx=(5, 0))

        # 출력 경로 선택
        self.output_path = tk.StringVar(value=self.data_dir)
        output_frame = ttk.Frame(self.main_frame)
        output_frame.pack(fill=tk.X, pady=5)
        ttk.Label(output_frame, text="출력 경로:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(output_frame, textvariable=self.output_path, width=40).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(output_frame, text="Browse", command=self.browse_output_path).pack(side=tk.LEFT, padx=(5, 0))

        # 파일 형식 선택
        format_frame = ttk.Frame(self.main_frame)
        format_frame.pack(fill=tk.X, pady=5)
        ttk.Label(format_frame, text="출력 형식:").pack(side=tk.LEFT, padx=(0, 5))
        self.format_combobox = ttk.Combobox(format_frame, values=["CSV", "JSON", "TXT"])
        self.format_combobox.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.format_combobox.set("CSV")  # 기본값 설정

        # 출력 버튼
        self.output_button = ttk.Button(self.main_frame, text="출력", command=self.output)
        self.output_button.pack(pady=10)

        # 상태 메시지
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, wraplength=500)
        self.status_label.pack(pady=10)

    def browse_file(self, file_type):
        if file_type == 'index':
            filetypes = [("Binary files", "*.bin"), ("All files", "*.*")]
            title = "Select Index File"
        else:
            filetypes = [("Pickle files", "*.pkl"), ("All files", "*.*")]
            title = "Select Metadata File"

        filename = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes,
            initialdir=self.data_dir
        )
        if filename:
            if file_type == 'index':
                self.index_path.set(filename)
            else:
                self.meta_path.set(filename)

    def browse_output_path(self):
        path = filedialog.askdirectory(initialdir=self.data_dir)
        if path:
            self.output_path.set(path)

    def output(self):
        meta_path = self.meta_path.get()
        output_path = self.output_path.get()
        format = self.format_combobox.get()

        if not meta_path:
            self.status_var.set("Metadata 파일을 선택해주세요.")
            return

        try:
            # 출력 디렉토리가 존재하지 않으면 생성
            os.makedirs(output_path, exist_ok=True)
            
            # 메타데이터 로드
            with open(meta_path, 'rb') as f:
                metadata = pickle.load(f)

            # 파일로 출력할 준비
            file_name = f'vdb_metadata_output.{format.lower()}'
            full_path = os.path.join(output_path, file_name)

            if format == 'CSV':
                with open(full_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for meta in metadata:
                        writer.writerow([json.dumps(meta, ensure_ascii=False)])
            elif format == 'JSON':
                with open(full_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
            elif format == 'TXT':
                with open(full_path, 'w', encoding='utf-8') as f:
                    for meta in metadata:
                        f.write(f"{json.dumps(meta, ensure_ascii=False)}\n")
            else:
                raise ValueError(f"지원하지 않는 형식입니다: {format}")

            messagebox.showinfo("성공", f"메타데이터를 {full_path}로 저장했습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"메타데이터 출력 중 오류 발생: {str(e)}")

    def on_closing(self):
        window_config = {
            'width': self.window.winfo_width(),
            'height': self.window.winfo_height(),
            'x': self.window.winfo_x(),
            'y': self.window.winfo_y()
        }
        self.config['vdb_selector'] = window_config
        self.window.destroy()