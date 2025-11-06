# slide_registry.py
from typing import Callable, Dict, List

SlideFunc = Callable[[object], None]
_registry: Dict[int, SlideFunc] = {}

def slide(number: int):
    """Decorator to register a slide function under a numeric index."""
    def _wrap(fn: SlideFunc) -> SlideFunc:
        if number in _registry:
            raise ValueError(f"Slide #{number} already registered by {_registry[number].__name__}")
        _registry[number] = fn
        return fn
    return _wrap

def all_numbers() -> List[int]:
    return sorted(_registry.keys())

def get(number: int) -> SlideFunc:
    return _registry[number]
