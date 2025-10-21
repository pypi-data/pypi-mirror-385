from abc import ABC, abstractmethod
from typing import Any

class BaseCommand(ABC):
    """Base class for device commands"""
    
    def __init__(self, device_manager):
        self.device = device_manager
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute command - must be implemented by subclasses"""
        pass