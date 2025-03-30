import os

import psutil
from datetime import datetime

def get_memory_usage() -> float:
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def calculate_processing_time(start_time: datetime) -> int:
    return int((datetime.now() - start_time).total_seconds() * 1000)