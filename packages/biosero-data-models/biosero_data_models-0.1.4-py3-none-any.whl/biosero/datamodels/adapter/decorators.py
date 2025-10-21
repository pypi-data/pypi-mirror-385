import logging
from biosero.datamodels.adapter.template_icons import Icons
from rich.logging import RichHandler
import functools

logger = logging.getLogger("rich")
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

def parameter(name=None, inputs=None, outputs=None, icon=Icons.CODE.value, category="Python", color="#FFFFFF"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result

        # Attach the metadata to the wrapper function
        wrapper._parameter_decorator = {
            'name': name,
            'inputs': inputs,
            'outputs': outputs,
            'icon': icon,
            'category': category,
            'color': color
        }
        
        return wrapper
    
    return decorator

def action(name=None):
    def decorator(func):
        @functools.wraps(func)  # Apply the wraps decorator here
        def wrapper(*args, **kwargs):
            logger.info(f"[blue]Action: {func.__name__} is being executed.[/blue]", extra={"markup": True})
            result = func(*args, **kwargs)
            return result
        
        # Attach the metadata to the wrapper function
        wrapper._action_decorator = {
            'name': name or func.__name__,
            'inputs': [],
            'outputs': []
        }
        
        return wrapper
    
    return decorator
