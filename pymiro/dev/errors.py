"""
Custom error formatter for pymiro.
"""
import sys
import traceback
from typing import Type
from types import TracebackType

def _get_hint(exc_type: Type[BaseException], exc_value: BaseException) -> list[str]:
    name = exc_type.__name__
    if name == "ComponentError":
        return [
            "Hint: return a VNode from your component",
            "      e.g. return Div(Text(\"hello\"))"
        ]
    elif name == "CycleError":
        return [
            "Hint: a computed value cannot depend on itself"
        ]
    elif "key" in str(exc_value).lower():
        # Handle "Missing key warn" or duplicate key errors
        return [
            "Hint: add key= props to list children"
        ]
    return []

def _format_error_box(title: str, lines: list[str]) -> str:
    min_width = 48
    max_line_len = max([len(line) for line in lines] + [len(title) + 6])
    width = max(min_width, max_line_len + 4)
    
    top = f"╔══ {title} "
    top += "═" * max(0, width - len(top) - 1) + "╗"
    
    body = ""
    for line in lines:
        if line == "":
            body += f"║ {'':<{width - 4}} ║\n"
        else:
            padded = f"{line:<{width - 4}}"
            body += f"║ {padded} ║\n"
            
    bottom = "╚" + "═" * (width - 2) + "╝"
    return f"{top}\n{body}{bottom}"

def pymiro_excepthook(exc_type: Type[BaseException], exc_value: BaseException, tb: TracebackType | None) -> None:
    # We only format pymiro-specific errors if possible, but the prompt says "on any pymiro exception"
    # and gives examples ComponentError and CycleError.
    name = exc_type.__name__
    is_pymiro_error = (
        name in ("ComponentError", "CycleError") or 
        "pymiro" in str(exc_type) or
        "key" in str(exc_value).lower()
    )
    
    if is_pymiro_error:
        # Extract function name from traceback if possible
        extracted = traceback.extract_tb(tb)
        func_name = "Unknown"
        if extracted:
            func_name = extracted[-1].name
            
        title = "pymiro error"
        lines = [
            f"{name} in {func_name}",
            str(exc_value),
            ""
        ]
        
        hints = _get_hint(exc_type, exc_value)
        if hints:
            lines.extend(hints)
            
        print(_format_error_box(title, lines), file=sys.stderr)
    else:
        sys.__excepthook__(exc_type, exc_value, tb)

def install_error_handler() -> None:
    sys.excepthook = pymiro_excepthook

__all__ = ["install_error_handler"]
