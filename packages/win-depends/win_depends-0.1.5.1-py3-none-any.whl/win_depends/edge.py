import os

class DependencyEdge:
    def __init__(self, parent, child, delay_loaded=False, missing=False, invalid=False):
        self.parent = parent
        self.child = child
        self.delay_loaded = delay_loaded
        self.missing = missing
        self.invalid = invalid
        self.in_cycle = False

    def __hash__(self):
        return hash((self.parent, self.child))

    def __eq__(self, other):
        return isinstance(other, DependencyEdge) and self.parent == other.parent and self.child == other.child

    def status_emojis(self):
        flags = []
        if self.missing:
            flags.append("❌")
        if self.invalid:
            flags.append("❗")
        if self.delay_loaded:
            flags.append("⏳")
        if self.in_cycle:
            flags.append("🔁")
        return flags

    def status_flags(self):
        flags = []
        if self.missing:
            flags.append("[MISSING]")
        if self.invalid:
            flags.append("[INVALID]")
        if self.delay_loaded:
            flags.append("[DELAY]")
        return flags

    def status_color(self):
        if self.missing:
            return "red"
        if self.invalid:
            return "orange"
        if self.delay_loaded:
            return "blue"
        return "black"
