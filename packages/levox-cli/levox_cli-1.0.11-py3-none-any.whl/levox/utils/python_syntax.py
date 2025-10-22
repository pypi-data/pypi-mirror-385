"""
Utilities to normalize modern Python syntax into forms parsable by Python 3.11's ast.

Specifically targets PEP 695 style type parameter syntax like:
  - class Name[T](...): -> class Name(...):
  - def func[T](...): -> def func(...):

The goal is to allow static parsing for analysis only; semantics are not executed.
"""

import re
from typing import Final


_CLASS_TYPE_PARAMS_RE: Final = re.compile(r"(\bclass\s+\w+)\s*\[[^\]]+\](\s*\(.*?\))?\s*:")
_DEF_TYPE_PARAMS_RE: Final = re.compile(r"(\bdef\s+\w+)\s*\[[^\]]+\](\s*\(.*?\))\s*:")


def normalize_modern_syntax(content: str) -> str:
    """Rewrite select modern constructs to be compatible with Python 3.11 ast.parse.

    - Removes type parameter brackets on class and function definitions.
    - Leaves all other code intact.
    """
    if not content or ("[" not in content and "]" not in content):
        return content

    # Class type parameters -> remove generic bracket segment
    content = _CLASS_TYPE_PARAMS_RE.sub(r"\1\2:", content)

    # Function type parameters -> remove generic bracket segment
    content = _DEF_TYPE_PARAMS_RE.sub(r"\1\2:", content)

    return content


