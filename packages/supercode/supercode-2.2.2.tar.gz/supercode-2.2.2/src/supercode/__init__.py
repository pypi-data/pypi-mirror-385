"""
SuperCode - 简单脚本解释器
"""

from .core import Compiler, Compiler_Code, set_func, set_block_handler, main, safe_eval

__version__ = "2.0.0"
__author__ = "王子毅"

__all__ = [
    'Compiler',
    'Compiler_Code', 
    'set_func',
    'set_block_handler',
    'main',
    'safe_eval'
]