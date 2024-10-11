import json
import os
import sys

# 프로젝트 루트 디렉토리 경로 설정
if getattr(sys, 'frozen', False):
    # PyInstaller로 실행 파일을 만든 경우
    PROJECT_ROOT = os.path.dirname(sys.executable)
else:
    # 일반적인 Python 스크립트로 실행하는 경우
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Good DBMgr 폴더 경로 설정
GOOD_DBMGR_PATH = os.path.join(PROJECT_ROOT, 'Good DBMgr')
CONFIG_FILE = os.path.join(GOOD_DBMGR_PATH, "config.json")

def save_config(window, settings):
    """
    설정을 저장하는 함수
    """
    config = {
        "width": window.winfo_width(),
        "height": window.winfo_height(),
        "x": window.winfo_x(),
        "y": window.winfo_y(),
        "font_family": settings.get("font_family", "Arial"),
        "font_size": settings.get("font_size", 10),
        "theme": settings.get("theme", "arc"),
        "button_style": settings.get("button_style", "default"),
        "vdb_creator": settings.get("vdb_creator", {}),
        "vdb_selector": settings.get("vdb_selector", {}),
        "vdb_retriever": settings.get("vdb_retriever", {}),
        "vdb_merge": {"width": 400, "height": 300, "x": 250, "y": 250},
        "api_key": settings.get("api_key", {}),
        "settings": settings.get("settings", {})
    }
    # Good DBMgr 폴더가 없으면 생성
    os.makedirs(GOOD_DBMGR_PATH, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def load_config():
    """
    설정을 불러오는 함수
    """
    default_config = {
        "width": 600,
        "height": 400,
        "x": 100,
        "y": 100,
        "font_family": "Arial",
        "font_size": 10,
        "theme": "arc", 
        "button_style": "default",
        "vdb_creator": {"width": 600, "height": 500, "x": 150, "y": 150},
        "vdb_selector": {"width": 400, "height": 300, "x": 200, "y": 200},
        "vdb_retriever": {"width": 400, "height": 300, "x": 250, "y": 250},
        "vdb_merge": {"width": 400, "height": 300, "x": 250, "y": 250},
        "api_key": {"width": 500, "height": 400, "x": 300, "y": 300},
        "settings": {"width": 300, "height": 250, "x": 350, "y": 350}
    }
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding='utf-8') as f:
            return {**default_config, **json.load(f)}
    return default_config

def save_module_config(module_name, config):
    """
    특정 모듈의 설정을 저장하는 함수
    """
    full_config = load_config()
    full_config[module_name] = config
    with open(CONFIG_FILE, "w", encoding='utf-8') as f:
        json.dump(full_config, f, ensure_ascii=False, indent=4)

def load_module_config(module_name):
    """
    특정 모듈의 설정을 불러오는 함수
    """
    full_config = load_config()
    return full_config.get(module_name, {})