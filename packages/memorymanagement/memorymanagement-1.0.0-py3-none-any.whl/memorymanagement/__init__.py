"""
Provides memory management support.

---
## Module `cleaning`
The class `Cleaner` flags the global references to erase them when commanded. References can be chosen to be excluded or included again in the process.
## Module `pointers`
A safe implementation of pointers for Python. Written in pure Python, this module includes two things:
### 1. Class `Pointer`
Creates a `Pointer` instance. These pointers point to a reference, not to an object in memory.
If value for the reference is changed, so is the pointer value and *viceversa*.
### 2. Decorator `pointerize`
Allows a function to receive pointers instead of the normally expected values.
"""
# Imports
from .cleaning import Cleaner
from .pointers import Pointer,pointerize

# Declare "__all__"
__all__=["Cleaner","Pointer","pointerize"]