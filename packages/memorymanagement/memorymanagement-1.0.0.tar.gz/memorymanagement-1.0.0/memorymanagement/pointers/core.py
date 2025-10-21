# Import "TypeVar" and "Generic"
from typing import TypeVar,Generic
# Import "modules" from "sys" package
from sys import modules
# Import "currentframe" from "inspect" package
from inspect import currentframe

# Create new generic type
object_type=TypeVar("object_type")
# Define the class "Pointer"
class Pointer(Generic[object_type]):
    """
    Implements pointers in Python for both mutable (though unneded) and non-mutable objects.
    These pointers are completely safe and do not work internally as C's pointers, they are just an imitation of their behaviour.
    
    When a Pointer instance is created, though it stores a value, it "points" to an specific reference, not the value in a memory adress.
    This way, all references pointing to the same non-mutable object don't change when the pointer is updated, avoiding a potential mess.
    
    Non-mutable objects still change their memory adresses when re-referenced but the reference and the value stored in the pointer are forced to share memory adress.
    
    Value and memory adress updates are not made in real-time, but the methods update the non-coincident values:
        * **Getter**: it updates its own value to the variable's one (if variable was given instead of literal).
        * **Setter**: it updates the value of the variable to its own (if variable was given instead of literal).
        * **Deleter**: it also deletes the original variable (if variable was given instead of literal).
    ---
    Attributes:
        value (`Any`, Hidden): Object to point to.
        attr (`str`|`None`, Hidden): Attribute of class instance. Only if `value` is a class instance.
        name (`str`, Hidden): Name of the global variable to which the pointer is pointing.
            Could require an input from the user to introduce the name of the variable if more than one is found.
        vars_dict (`dict[str,Any]`, Hidden): Dictionary of variables.
            `vars(modules["__main__"])` if pointing to a global variable and `inspect.currentframe().f_back.f_locals` if pointing to a local variable.
    ---
    
    ## Methods
        1. **Getter**: Gets the value.
        2. **Setter**: Sets a new value.
        3. **Deleter**: Deletes the value.
    All three methods are part of the same property.
    ---
    ## Properties
        :value: *`MethodType`*
        Points to `value` (or `value.attr`). Called through `<instance>.value`. All three possible objects (getter, setter and deleter) have been declared.
    
    ---
    
    ## Currently supported
    Both global and local variables can be pointed at.
    
    Literals are **not** supported because of it being useless. If you create a `Pointer` instance for a literal and works,
    keep in mind that it is merely by accident and it is **not** the intended use it was designed for.
    Currently, the only use for inserting a literal instead of a referenced value could be for the class code to display all the references pointing to that literal
    and bind the instance to the desired reference.
    """
    def __init__(self,value=None,attr:str|None=None,*,local:bool=False):
        """
        Arguments:
            value (`Any`,Optional): Object to point to. If want to point to a class instance atribute, introduce the class instance without the atribute.
            attr (`str`|`None`, Optional): Atribute of the class instance to which you want to point. Leave empty if `value` is not a class instance.
            local (`bool`, Optional): Indicates if the value to point to is a local variable (`True` for yes and `False` for no). `False` by default.
        """
        if local:
            vars_dict=currentframe().f_back.f_locals
        else:
            vars_dict=vars(modules["__main__"])
        self._value=value
        self._vars_dict=vars_dict
        self._attr=attr
        name=None
        name=[]
        for key,v in vars_dict.items():
            try:
                if v is value:
                    name.append(key)
            except ValueError:
                pass
        if len(name)>1:
            print(f"{name}\nMultiple variable names found for the 'value' parameter, introduce the correct one:")
            while True:
                name_aux=input()
                if name_aux in name:
                    break
                else:
                    print("Error, introduce the correct variable name for the 'value' parameter:")
            name=name_aux
            del name_aux
        elif len(name)==1:
            name=name[0]
        elif len(name)==0:
            name=None
        self._name=name
        return
    @property
    def value(self):
        if self._attr:
            if self._name and self._name not in list(self._vars_dict):
                del self._value,self._attr
                raise KeyError("The class instance has already been deleted, so the pointer no longer has access to it.")
            elif self._attr not in dir(self._value):
                raise AttributeError(f"The atribute '{self._attr}' has already been deleted, so the pointer no longer has access to it.")
            return getattr(self._value,self._attr)
        else:
            if self._name:
                if self._name not in list(self._vars_dict):
                    del self._value
                    raise KeyError("The variable has already been deleted, so the pointer no longer has access to it.")
                if self._value is not self._vars_dict[self._name]:
                    self._value=self._vars_dict[self._name]
            return self._value
    @value.setter
    def value(self,value):
        if self._attr:
            setattr(self._value,self._attr,value)
        else:
            self._value=value
            if self._name and value is not self._vars_dict[self._name]:
                self._vars_dict[self._name]=value
        return
    @value.deleter
    def value(self):
        if self._attr:
            delattr(self._value,self._attr)
        else:
            del self._value
            if self._name:
                del self._vars_dict[self._name]
        return