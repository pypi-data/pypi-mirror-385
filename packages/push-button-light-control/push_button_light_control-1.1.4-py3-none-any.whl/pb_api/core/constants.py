# Command Types (matches your HMI exactly)
CMD_CONTROL_MODE = 0x00  # 00 = Control Mode Command (3 bytes)
CMD_SETTING = 0x40       # 01 = Setting Command (15 bytes)  
CMD_OPERATING = 0x80     # 10 = Operating Command (15 bytes)
CMD_LUMIN = 0xC0         # 11 = Set Lumin Command (8 bytes)

# Control Modes (matches your HMI exactly)
CTRL_SW_STATE = 0b00000001
CTRL_SW_LUMIN = 0b00000011
CTRL_SW_AN0 = 0b00000101
CTRL_SW_PWM = 0b00001001
CTRL_UART = 0b00010000

CTRL_MODE_BYTES = {
    "SWITCH_MODE": CTRL_SW_STATE,
    "SWITCH_LUMIN_MODE": CTRL_SW_LUMIN,
    "ANALOG_MODE": CTRL_SW_AN0,
    "PWM_MODE": CTRL_SW_PWM,
    "UART_MODE": CTRL_UART
}

CTRL_MODES = {
    CTRL_SW_STATE: "SWITCH_MODE",
    CTRL_SW_LUMIN: "SWITCH_LUMIN_MODE", 
    CTRL_SW_AN0: "ANALOG_MODE", 
    CTRL_SW_PWM: "PWM_MODE",
    CTRL_UART: "UART_MODE"
}

# LED Positions
LED_UR = 0  # Upper Right
LED_UL = 1  # Upper Left
LED_LR = 2  # Lower Right
LED_LL = 3  # Lower Left

# Response Codes (matches your HMI exactly)
ACK_FIRMWARE_BASE = 0xC0  # Base for firmware release ACK
ACK_SUCCESS = 0xDD
NACK_INVALID_HEADER = 0x33
NACK_INVALID_DC = 0x34
NACK_INVALID_GS = 0x35
NACK_INVALID_MODE = 0x36
NACK_CHECKSUM_ERROR = 0x44

# Device Addressing
DEVICE_ID_MASK = 0x3F  # 00111111 - 6 bits for device ID
CMD_MASK = 0xC0        # 11000000 - 2 bits for command type
BROADCAST_ID = 0x00    # 00000000 - Broadcast to all devices
DEFAULT_DEVICE_ID = 0x3F  # 00111111 - Default device ID (all ones)
VALID_DEVICE_IDS = list(range(1, 63))  # 1-62

SETTING_PACKET_SIZE = 15
OPERATING_PACKET_SIZE = 15
LUMIN_PACKET_SIZE = 8

# Default Values
DC_MAX = 44
GS_MAX = 4095

# Color Presets (GBR format - matches your HMI exactly)
COLOR_BITS = {
    "OFF": (0, 0, 0),
    "RED": (0, 0, 1),
    "GREEN": (1, 0, 0),
    "BLUE": (0, 1, 0),
    "ORANGE": (1, 0, 1),
    "MAGENTA": (0, 1, 1),
    "CYAN": (1, 1, 0),
    "WHITE": (1, 1, 1),
}

COLOR_PRESETS = {
    "OFF": {'G': 0, 'B': 0, 'R': 0},
    "RED": {'G': 0, 'B': 0, 'R': 100},
    "GREEN": {'G': 100, 'B': 0, 'R': 0},
    "BLUE": {'G': 0, 'B': 100, 'R': 0},
    "ORANGE": {'G': 33, 'B': 0, 'R': 100},
    "MAGENTA": {'G': 0, 'B': 100, 'R': 100},
    "CYAN": {'G': 100, 'B': 100, 'R': 0},
    "WHITE": {'G': 100, 'B': 100, 'R': 100}
}

COLOR_PRESETS_DC = {
    "OFF": {'G': 0, 'B': 0, 'R': 0},
    "RED": {'G': 0, 'B': 0, 'R': 44},
    "GREEN": {'G': 44, 'B': 0, 'R': 0},
    "BLUE": {'G': 0, 'B': 44, 'R': 0},
    "ORANGE": {'G': 15, 'B': 0, 'R': 44},
    "MAGENTA": {'G': 0, 'B': 44, 'R': 44},
    "CYAN": {'G': 44, 'B': 44, 'R': 0},
    "WHITE": {'G': 44, 'B': 44, 'R': 44}
}

# Grayscale presets mapping (fL to %) - matches your HMI exactly
GS_PRESETS = {
    "OFF": 0,
    "NIGHT": 20,   # 20fL → 20%
    "DAY": 50,     # 150fL → 50%
    "MAX": 100     # MAX → 100%
}

# Renamed for clarity
LUMINOSITY_PRESETS = {
    "OFF": 0,
    "NIGHT": 20,   # 20fL → 20%
    "DAY": 50,     # 150fL → 50%
    "MAX": 100     # MAX → 100%
}

# Keep GS_PRESETS for backward compatibility, but recommend LUMINOSITY_PRESETS
GS_PRESETS = LUMINOSITY_PRESETS

# Light colors for UI display
LIGHT_COLORS = {
    "OFF": "#000000", "RED": "#FF4C4C", "GREEN": "#75FF75", "BLUE": "#4DBEFF",
    "ORANGE": "#FFC558", "MAGENTA": "#FF6BFF", "CYAN": "#8FFFFF", "WHITE": "#FFFFFF"
}

# Response handling
IGNORE_UNKNOWN_SINGLE_BYTES = True  # Set to False to see all unknown bytes