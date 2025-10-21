# Imports
from sys import settrace
from inspect import signature
from functools import wraps
from .core import Pointer

# Define the decorator
def pointerize(func):
    """
    Allows the decorated function to receive pointers instead of the normally expected values.
    
    The decorated function is still able to receive its normally expected parameters.
    
    ---
    Arguments:
        func (`FunctionType`): Decorated function.
    """
    # Makes the decorating function to keep its identity
    @wraps(func)
    # Define the wrapper
    def wrapper(*args,**kwargs):
        # Obtain the signature (parameters and defaults) of the decorated function
        sig=signature(func)
        # Bind call arguments to the signature
        bound=sig.bind(*args,**kwargs)
        # Defaults all the arguments which haven't been passed
        bound.apply_defaults()
        
        # Dictionary containing all the parameters
        param_map=bound.arguments
        
        # Dictionary containing only the parameters that are pointers
        pointer_map={
            name:val for name,val in param_map.items()
            if isinstance(val,Pointer)
        }
        
        # List containing all the positional arguments to be passed to the decorated function
        exec_args=[
            val.value if isinstance(val,Pointer) else val
            for val in bound.args
        ]
        # Dictionary containing all the keyword arguments to be passed to the decorated function
        exec_kwargs={
            k:v.value if isinstance(v,Pointer) else v
            for k,v in bound.kwargs.items()
        }
        
        # Empty dict, future source to update pointers' values
        frame_data={}
        
        # Tracer function compatible with the sys.settrace API
        def tracer(frame,event,arg):
            if event=="return" and frame.f_code is func.__code__:
                frame_data.update(frame.f_locals)
            return tracer
        # Activate tracing
        settrace(tracer)
        # We try to execute the function
        try:
            result=func(*exec_args,**exec_kwargs)
        # Even if the program meets an error
        finally:
            # It deactivates tracing
            settrace(None)
        # If no exception or error is raised, the program continues from here
        
        # Iterates through the pointers
        for name,ptr in pointer_map.items():
            # Checks if the parameter name is in the traced frame (of local variables of the decorated function)
            if name in frame_data:
                # In which case, the pointer's value is updated
                ptr.value=frame_data[name]
        # Return the result of the decorated function
        return result
    # Return the wrapper
    return wrapper