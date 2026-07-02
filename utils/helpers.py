from pathlib import Path

def get_file_size_mb(path : Path) -> float:
    return round(path.stat().st_size / (1024 * 1024), 2)