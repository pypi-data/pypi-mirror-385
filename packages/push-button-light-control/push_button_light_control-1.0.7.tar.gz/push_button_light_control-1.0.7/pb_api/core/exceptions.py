class PushButtonError(Exception):
    """Base exception for Push Button Light controller errors"""
    pass

class CommunicationError(PushButtonError):
    """Communication related errors with Push Button devices"""
    pass

class TimeoutError(PushButtonError):
    """Timeout errors when communicating with Push Button devices"""
    pass

class ProtocolError(PushButtonError):
    """Protocol parsing errors for Push Button communication"""
    pass

class DeviceError(PushButtonError):
    """Push Button device specific errors"""
    def __init__(self, error_code: int, message: str = None):
        self.error_code = error_code
        self.message = message or f"Push Button device error (Code: 0x{error_code:02x})"
        super().__init__(self.message)

class ConfigurationError(PushButtonError):
    """Push Button device configuration errors"""
    pass