import os
from functools import lru_cache

class DependencyNode:
    def __init__(self, path, is_system):
        # 假定path已为绝对路径
        self.path = path
        self.is_system = is_system
        self.orphan = False

    def __repr__(self):
        flags = []
        if self.is_system:
            flags.append("[SYS]")
        if self.orphan:
            flags.append("(orphan)")
        return f"{os.path.basename(self.path)}{''.join(flags)}"

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        return isinstance(other, DependencyNode) and self.path == other.path
