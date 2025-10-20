class Range:
    def __init__(self, min=None, max=None):
        self.min, self.max = min, max
    def __call__(self, value):
        if self.min is not None and value < self.min:
            raise ValueError(f"harus >= {self.min}")
        if self.max is not None and value > self.max:
            raise ValueError(f"harus <= {self.max}")
        return value

class OneOf:
    def __init__(self, choices):
        self.choices = list(choices)
    def __call__(self, value):
        if value not in self.choices:
            raise ValueError(f"harus salah satu dari {self.choices}")
        return value
