import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from configuration import save_module_config, load_module_config
from .merger import Merger
import os
import json
import pickle
from vdb_data.common_constants import VDB_DATA_DIR, ID_FILE_PATH

class VdbMergeModule:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.window = tk.Toplevel(parent)
        self.window.title("VDB Merge")
        
        # 저장된 설정 적용
        window_config = load_module_config('vdb_merge')
        self.window.geometry(f"{window_config.get('width', 600)}x{window_config.get('height', 500)}" \
                     f"+{window_config.get('x', 200)}+{window_config.get('y', 200)}")

        self.data_dir = VDB_DATA_DIR
        self.id_file_path = ID_FILE_PATH
        self.load_last_id()

        self.vdb1_index = tk.StringVar()
        self.vdb1_meta = tk.StringVar()
        self.vdb2_index = tk.StringVar()
        self.vdb2_meta = tk.StringVar()

        self.current_step = 1
        self.create_widgets()
        
        # 창 닫힐 때 설정 저장
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self.window, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_label = ttk.Label(self.main_frame, text="VDB Merge Module", font=('Helvetica', 16, 'bold'))
        self.title_label.pack(pady=10)

        self.step_label = ttk.Label(self.main_frame, text="Step 1:기준이 될 db를 선택해주세요.\n해당 파일의 last_id 뒤에 데이터가 따라 붙습니다.\n인덱스와 메타 파일을 둘 다 선택해주세요", font=('Helvetica', 12))
        self.step_label.pack(pady=5)

        # VDB1 선택
        self.vdb1_frame = ttk.Frame(self.main_frame)
        self.vdb1_frame.pack(fill=tk.X, pady=5)

        ttk.Label(self.vdb1_frame, text="VDB1 Index:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(self.vdb1_frame, textvariable=self.vdb1_index, width=40).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(self.vdb1_frame, text="Browse", command=lambda: self.browse_file('vdb1_index')).grid(row=0, column=2, padx=5, pady=2)

        ttk.Label(self.vdb1_frame, text="VDB1 Metadata:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(self.vdb1_frame, textvariable=self.vdb1_meta, width=40).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(self.vdb1_frame, text="Browse", command=lambda: self.browse_file('vdb1_meta')).grid(row=1, column=2, padx=5, pady=2)

        # VDB2 선택 (초기에는 숨김)
        self.vdb2_frame = ttk.Frame(self.main_frame)

        ttk.Label(self.vdb2_frame, text="VDB2 Index:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(self.vdb2_frame, textvariable=self.vdb2_index, width=40).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(self.vdb2_frame, text="Browse", command=lambda: self.browse_file('vdb2_index')).grid(row=0, column=2, padx=5, pady=2)

        ttk.Label(self.vdb2_frame, text="VDB2 Metadata:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(self.vdb2_frame, textvariable=self.vdb2_meta, width=40).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(self.vdb2_frame, text="Browse", command=lambda: self.browse_file('vdb2_meta')).grid(row=1, column=2, padx=5, pady=2)

        # 버튼 프레임
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)

        self.next_button = ttk.Button(self.button_frame, text="다음으로", command=self.next_step)
        self.next_button.pack(side=tk.LEFT, padx=5)

        self.merge_button = ttk.Button(self.button_frame, text="병합", command=self.merge_vdbs, state=tk.DISABLED)
        self.merge_button.pack(side=tk.LEFT, padx=5)

        self.close_button = ttk.Button(self.button_frame, text="닫기", command=self.on_closing)
        self.close_button.pack(side=tk.LEFT, padx=5)

        # 상태 메시지
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, wraplength=500)
        self.status_label.pack(pady=10)

    def browse_file(self, file_type):
        if file_type.endswith('index'):
            filetypes = [("Binary files", "*.bin"), ("All files", "*.*")]
            title = "인덱스 파일을 선택해주세요"
        else:
            filetypes = [("Pickle files", "*.pkl"), ("All files", "*.*")]
            title = "메타 파일을 선택해주세요"

        initial_dir = self.data_dir if os.path.exists(self.data_dir) else os.path.dirname(self.data_dir)

        filename = filedialog.askopenfilename(
            title=title,
            filetypes=filetypes,
            initialdir=initial_dir
        )
        if filename:
            getattr(self, file_type).set(filename)

    def next_step(self):
        if self.current_step == 1:
            if not self.vdb1_index.get() or not self.vdb1_meta.get():
                self.status_var.set("첫번째 db의 인덱스와 메타 파일을 둘 다 선택해주세요")
                return
            self.current_step = 2
            self.step_label.config(text="Step 2: 병할될 DB를 선택해주세요\n인덱스와 메타 파일을 둘 다 선택해주세요")
            self.vdb2_frame.pack(fill=tk.X, pady=5, before=self.button_frame)
            self.next_button.config(state=tk.DISABLED)
            self.merge_button.config(state=tk.NORMAL)

    def load_last_id(self):
        if os.path.exists(self.id_file_path):
            with open(self.id_file_path, 'r') as f:
                data = json.load(f)
                self.last_id = data.get('last_id', 0)
        else:
            self.last_id = 0

    def save_last_id(self, last_id):
        with open(self.id_file_path, 'w') as f:
            json.dump({'last_id': last_id}, f)

    def merge_vdbs(self):
        if not self.vdb2_index.get() or not self.vdb2_meta.get():
            self.status_var.set("두 DB의 인덱스와 메타 데이터를 모두 선택해주세요")
            return
        
        try:
            output_dir = filedialog.askdirectory(title="출력 디렉토리를 선택해주세요", initialdir=self.data_dir)
            if not output_dir:
                return  
            
            self.status_var.set("vdb 병합중입니다.")
            self.window.update()  
            
            # 머지 시작
            merged_index_path, merged_meta_path = Merger.merge_vdbs(
                self.vdb1_index.get(), self.vdb1_meta.get(),
                self.vdb2_index.get(), self.vdb2_meta.get(),
                output_dir
            )
            
            # 머지 적용
            if Merger.verify_merge(merged_index_path, merged_meta_path):
                # 메타데이터에서 최대 data_id 찾기
                with open(merged_meta_path, 'rb') as f:
                    merged_meta = pickle.load(f)
                max_data_id = max(item['data_id'] for item in merged_meta)
                
                # last_id 업데이트 및 저장
                self.save_last_id(max_data_id)
                
                self.status_var.set(f"출력된 경로: {output_dir}")
                messagebox.showinfo("병합 성공", 
                                    f"성공적으로 병합되었습니다.\n"
                                    f"last_id가 {max_data_id}로 업데이트되었습니다.\n\n"
                                    f"Merged index: {merged_index_path}\n"
                                    f"Merged metadata: {merged_meta_path}")
            else:
                self.status_var.set("병합 검증에 실패하였습니다. 출력 파일을 확인해주세요.")

        except Exception as e:
            self.status_var.set(f"병합 중 에러가 발생했습니다: {str(e)}")
            messagebox.showerror("Merge Error", str(e))

    def on_closing(self):
        window_config = {
            'width': self.window.winfo_width(),
            'height': self.window.winfo_height(),
            'x': self.window.winfo_x(),
            'y': self.window.winfo_y()
        }
        save_module_config('vdb_merge', window_config)
        self.window.destroy()