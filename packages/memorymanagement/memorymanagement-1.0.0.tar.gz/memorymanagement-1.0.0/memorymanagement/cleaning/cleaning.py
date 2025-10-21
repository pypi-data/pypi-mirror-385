# Imports
from sys import modules

# Define the class "Cleaner"
class Cleaner:
    """
    Class for references management. It keeps track of the names of the global variables to be deleted and deletes them when ordered.
    
    The cleaning process only deletes the flagged references to objects, but doesn't directly force the garbage collector to destroy the objects they are pointing to.
    
    ---
    ## WARNING
    THERE CAN ONLY BE **ONE** CLEANER OBJECT.\n
    Initializing a new one will delete all global references to the previous one.
    
    ---
    Attributes:
        _not_delete (`list[str]`, Hidden): List of variables to never delete from memory. These cannot be included in the process even if ordered so.\n
            These mainly are variables needed for the system to work and imports.
        _excluded (`list[str]`, Hidden): List of variables excluded from the memory cleaning that can be included again if desired.
        _flagged (`list[str]`, Hidden): List of variables to erase from memory. Variables can be put in and/or taken out through methods.
    ---
    
    ## Methods
        :update: *`MethodType`*
        Updates the list of variables to erase from memory including all the new variables global variables not manually excluded.\n
            It also allows to incorporate previously excluded variables.
        :exclude: *`MethodType`*
        Allows you to exclude variables from the cleaning process without need to use the `instance.update()` method.
        :include: *`MethodType`*
        Allows you to include variables in the cleaning process without need to use the `instance.update()` method.
        :clean: *`MethodType`*
        Erases all the flagged references from memory.
    ---
    
    ## Properties
        :not_delete: *`MethodType`*, *Getter*
        Returns the list of variables that shouldn't be deleted and can't be included in the cleaning process.
        :excluded: *`MethodType`*, *Getter*
        Returns the list of variables excluded from the cleaning process but can be included again if ordered.
        :flagged: *`MethodType`*, *Getter*
        Returns the list of variables to be erased from memory.
    None of this properties has setter or deleter. Those lists can only be manipulated through the class methods.
    """
    def __init__(self,not_delete:list[str]=list(vars(modules["__main__"])),excluded:list[str]=[],flagged:list[str]=[]):
        """
        Initializes the class instance.\n
        It is recommended to initialize the instance right after all global imports at the beggining of the program so no argument is needed.
        
        ---
        Arguments:
            not_delete (`list[str]`, Optional): List of variables to never be deleted. It takes the list of global variables of the main module by default.
            excluded (`list[str]`, Optional): List of variables to be excluded from the memory cleaning process. Empty list by default.
            flagged (`list[str]`, Optional): List of variables to be erased from memory. Empty list by default.
        """
        for key,value in vars(modules["__main__"]).copy().items():
            if isinstance(value,Cleaner) and key in vars(modules["__main__"]).keys():
                del vars(modules["__main__"])[key]
        self._not_delete=not_delete.copy()
        self._excluded=excluded.copy()
        self._flagged=flagged.copy()
        return
    def update(self,exclude:str|list[str]|tuple[str]|None=None,include:str|list[str]|tuple[str]|None=None):
        """
        Flags all the new global variables' references that were not manually excluded here or before. You can also include previously excluded references.
        
        ---
        Arguments:
            exclude (`str`|`list[str]`|`tuple[str]`|`None`, Optional): Allows you to exclude a single (`str`) or multiple (`list` or `tuple`) variables.
                `None` by default.
            include (`str`|`list[str]`|`tuple[str]`|`None`, Optional): Allows you to include a single (`str`) or multiple (`list` or `tuple`) variables.
                `None` by default.
        """
        if exclude:
            if isinstance(exclude,str):
                exclude=[exclude]
            self._excluded.extend([var for var in exclude if var not in self._excluded])
        if include:
            if isinstance(include,str):
                include=[include]
            for var in include:
                while var in self._excluded:
                    self._excluded.remove(var)
        self._flagged=[var for var in list(vars(modules["__main__"])) if var not in self._not_delete and var not in self._excluded]
        return
    @property
    def not_delete(self):
        return self._not_delete
    @property
    def excluded(self):
        return self._excluded
    @property
    def flagged(self):
        return self._flagged
    def exclude(self,*exclude:str):
        """
        Allows to exclude the desired references from the cleaning process.
        
        ---
        Arguments:
            *exclude (`str`): Stream of references to be excluded.
        """
        for var in exclude:
            while var in self._flagged:
                self._flagged.remove(var)
            if var not in self._excluded:
                self._excluded.append(var)
        return
    def include(self,*include:str):
        """
        Allows to include the desired references (previously excluded) in the cleaning process.
        
        ---
        Arguments:
            *include (`str`): Stream of references to be included.
        """
        for var in include:
            if var not in self._flagged:
                self._flagged.append(var)
            while var in self._excluded:
                self._excluded.remove(var)
        return
    def clean(self):
        """
        Culminates the cleaning process. Erases all the flagged references.
        """
        for var in self._flagged:
            if var in list(vars(modules["__main__"])):
                del vars(modules["__main__"])[var]
        self._flagged.clear()
        return