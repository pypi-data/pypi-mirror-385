"""
Matsh - библиотека для работы с DeepSeek через OpenRouter
"""

from .core import depsek1, depsek2, add_api_key_to_pool1, add_api_key_to_pool2, get_pool_stats

__version__ = "0.1.2"
__all__ = [
    "depsek1",
    "depsek2",
    "add_api_key_to_pool1",
    "add_api_key_to_pool2",
    "get_pool_stats"
]