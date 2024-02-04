from .imports import By
from typing import Optional
import time
import random


def wait_element(min_sec: Optional[float] = 4.0, max_sec: Optional[float] = 8.0) -> None:
    if min_sec is None:
        min_sec = 4.0
    if max_sec is None or max_sec < min_sec:
        max_sec = max(min_sec, 8.0)
    
    time.sleep(random.uniform(min_sec, max_sec))

    