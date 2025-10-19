from dataclasses import dataclass
import os
from typing import List


@dataclass
class ConfigData:
    search_paths: List[str] = "."
    patterns: List[str] = "*~", ".*~"
    recursive: bool = True
    ignore: List[str | os.PathLike] = ".cache", "__pycache__", ".git", "node_modules"
