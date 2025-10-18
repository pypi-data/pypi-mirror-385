import base64
import os
from pathlib import Path

import comfykit

# Package installation path (for accessing package resources)
SRC_PATH = Path(comfykit.__file__).parent

def get_comfykit_root_path() -> str:
    """Get ComfyKit root path - current working directory"""
    return str(Path.cwd())

def ensure_comfykit_root_path() -> str:
    """Ensure ComfyKit root path exists and return the path"""
    root_path = get_comfykit_root_path()
    root_path_obj = Path(root_path)

    # Check if this is first time initialization in this directory
    data_dir = root_path_obj / 'data'
    if not data_dir.exists():
        from rich.console import Console
        console = Console()
        console.print(f"🎯 [bold blue]Initializing ComfyKit in root path:[/bold blue] {root_path}")
        console.print("💡 This directory will store your configurations, workflows, and generated files.\n")

    # Create directory structure if needed
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / 'custom_workflows').mkdir(exist_ok=True)
    (data_dir / 'custom_starters').mkdir(exist_ok=True)

    return root_path

def get_root_path(*paths: str) -> str:
    """Get path relative to ComfyKit root path"""
    root_path = ensure_comfykit_root_path()
    if paths:
        return os.path.join(root_path, *paths)
    return root_path

def get_data_path(*paths: str) -> str:
    """Get path relative to ComfyKit root path data folder"""
    if paths:
        return get_root_path("data", *paths)
    return get_root_path("data")

def get_src_path(*paths: str) -> str:
    """Get path relative to package source (for accessing package resources)"""
    if paths:
        return os.path.join(SRC_PATH, *paths)
    return str(SRC_PATH)

def get_temp_path(*paths: str) -> str:
    """Get path relative to ComfyKit root path temp folder"""
    temp_path = get_root_path("temp")
    if paths:
        return os.path.join(temp_path, *paths)
    return temp_path

def save_base64_to_file(base64_str, file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(base64_str))
