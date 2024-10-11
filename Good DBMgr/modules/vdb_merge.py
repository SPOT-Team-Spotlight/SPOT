import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from configuration import save_module_config, load_module_config
from .merger import Merger
import os

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

        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.project_root, 'data')

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

        self.step_label = ttk.Label(self.main_frame, text="Step 1: 첫 번째 DB를 선택해주세요", font=('Helvetica', 12))
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

        initial_dir = self.data_dir if os.path.exists(self.data_dir) else self.project_root

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
            self.step_label.config(text="Step 2: 두 번째 DB를 선택해주세요")
            self.vdb2_frame.pack(fill=tk.X, pady=5, before=self.button_frame)
            self.next_button.config(state=tk.DISABLED)
            self.merge_button.config(state=tk.NORMAL)

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
                self.status_var.set(f"VDBs successfully merged. Output saved to {output_dir}")
                messagebox.showinfo("Merge Successful", f"VDBs have been successfully merged.\nMerged index: {merged_index_path}\nMerged metadata: {merged_meta_path}")
            else:
                self.status_var.set("Merge verification failed. Please check the output files.")
        
        except Exception as e:
            self.status_var.set(f"Error during merge: {str(e)}")
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