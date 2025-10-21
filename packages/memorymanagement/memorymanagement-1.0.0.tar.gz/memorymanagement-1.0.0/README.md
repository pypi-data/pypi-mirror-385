# `memorymanagement`
Provides memory management support.
## Modules
### `cleaning`
Provides the class `Cleaner`, which allows you to flag references stored in memory to eventually erase them.
It is also possible to modify the list of flagged references through its methods.
### `pointers`
Provides a safe implementation of pointers for Python.
#### Class `Pointer`
The pointer itself. Imitates the behaviour of C pointers. This pointer points to a reference, not to an object stored in memory.
#### Decorator `pointerize`
Allows functions to receive pointers instead of values.
## Installation
You can install the `memorymanager` package from PyPI as follows:
```bash
pip install memorymanagement
```
You can also install the `memorymanager` package (Test PyPI versión of `memorymanager`) from TestPyPI as follows:
```bash
pip install --index-url https://test.pypi.org/simple/ memorymanager
```
For TestPyPI versión, `--no-deps` option is not needed because it has no dependencies.
## How to use
### Class `Cleaner`
```py
# Imports
# Make your imports here
from memorymanagement import Cleaner # Importing class Cleaner
```
Right after imports are done, I recommend to initialize an instance of class `Cleaner`, so no arguments are needed. This is the optimal use this class was designed for.
```py
# Initialize cleaner object
cleaner=Cleaner()
```
Create, for example, these global variables:
```py
value_1=10
value_2=50
value_3=100
```
Update the list of flagged references like one of the following:
* Including all new global variables:
    ```py
    cleaner.update()
    print(cleaner.flagged)
    ```
    Output:
    ```sh
    ["value_1","value_2","value_3"]
    ```
* Excluding some variables:
    ```py
    cleaner.update(exclude="value_2")
    print(cleaner.flagged)
    ```
    Output:
    ```sh
    ["value_1","value_3"]
    ```
    ---
    ```py
    cleaner.update(exclude=["value_2","value_3"])
    print(cleaner.flagged)
    ```
    Output:
    ```sh
    ["value_1"]
    ```
* Include again some variables:

    After having excluded some variables
    ```py
    cleaner.update(exclude=["value_2","value_3"])
    ```
    You can reintroduce them
    ```py
    # Create a new variable and update
    value_4=150
    cleaner.update(exclude="value_4",include="value_2") # "include" can also be a list of strings
    print(cleaner.flagged)
    ```
    Output:
    ```sh
    ["value_1","value_2"]
    ```
You can also directly include or exclude references like so:
```py
cleaner.exclude(<name_var_1>,<name_var_2>,...)
```
```py
cleaner.include(<name_var_1>,<name_var_2>,...)
```
### Class `Pointer`
Example:
```py
from memorymanagement import Pointer
a=10
x=Pointer(a)
print(f"a:\n{a}\n\nPointer:\n{x.value}\n\n")
a=20
print(f"a:\n{a}\n\nPointer:\n{x.value}\n\n")
a=10
x.value=20
print(f"a:\n{a}\n\nPointer:\n{x.value}")
```
Output:
```sh
a:
10

Pointer:
10


a:
20

Pointer:
20


a:
20

Pointer:
20
```
### Decorator `pointerize`
Example:
```py
from memorymanagement import pointerize
@pointerize
def myFunction(value:int):
    value=20
    return
a=10
print(f"Value: {a}")
myFunction(Pointer(a))
print(f"Value: {a}")
```
Output:
```sh
Value: 10
Value: 20

```
