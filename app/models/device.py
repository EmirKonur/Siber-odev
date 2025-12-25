"""
Device Models - Represents city infrastructure devices
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class DeviceStatus(Enum):
    """Device operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class DeviceType(Enum):
    """Types of city infrastructure devices"""
    STREET_LIGHT = "StreetLight"
    TRAFFIC_SIGNAL = "TrafficSignal"
    SECURITY_CAMERA = "SecurityCamera"
    WATER_METER = "WaterMeter"
    POWER_METER = "PowerMeter"


@dataclass
class Device(ABC):
    """
    Abstract base class for all city infrastructure devices.
    Uses Template Method pattern for common operations.
    """
    device_id: str
    name: str
    device_type: DeviceType = None
    status: DeviceStatus = DeviceStatus.INACTIVE
    location: str = "Unknown"
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.device_id:
            self.device_id = str(uuid.uuid4())
    
    @abstractmethod
    def activate(self) -> bool:
        """Activate the device"""
        pass
    
    @abstractmethod
    def deactivate(self) -> bool:
        """Deactivate the device"""
        pass
    
    @abstractmethod
    def get_status_info(self) -> dict:
        """Get detailed status information"""
        pass
    
    def update_status(self, status: DeviceStatus) -> None:
        """Update device status"""
        self.status = status
        self.last_updated = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert device to dictionary"""
        return {
            'device_id': self.device_id,
            'name': self.name,
            'type': self.device_type.value if self.device_type else 'Unknown',
            'status': self.status.value,
            'location': self.location,
            'last_updated': self.last_updated.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class StreetLight(Device):
    """Street light device with brightness control"""
    brightness: int = 0  # 0-100
    auto_mode: bool = True
    
    def __post_init__(self):
        super().__post_init__()
        self.device_type = DeviceType.STREET_LIGHT
    
    def activate(self) -> bool:
        """Turn on the street light"""
        self.status = DeviceStatus.ACTIVE
        self.brightness = 100
        self.last_updated = datetime.now()
        return True
    
    def deactivate(self) -> bool:
        """Turn off the street light"""
        self.status = DeviceStatus.INACTIVE
        self.brightness = 0
        self.last_updated = datetime.now()
        return True
    
    def set_brightness(self, level: int) -> bool:
        """Set brightness level (0-100)"""
        if 0 <= level <= 100:
            self.brightness = level
            self.status = DeviceStatus.ACTIVE if level > 0 else DeviceStatus.INACTIVE
            self.last_updated = datetime.now()
            return True
        return False
    
    def get_status_info(self) -> dict:
        """Get street light status"""
        info = self.to_dict()
        info.update({
            'brightness': self.brightness,
            'auto_mode': self.auto_mode
        })
        return info


@dataclass
class TrafficSignal(Device):
    """Traffic signal device with signal state control"""
    current_signal: str = "red"  # red, yellow, green
    cycle_duration: int = 60  # seconds
    
    def __post_init__(self):
        super().__post_init__()
        self.device_type = DeviceType.TRAFFIC_SIGNAL
    
    def activate(self) -> bool:
        """Activate traffic signal"""
        self.status = DeviceStatus.ACTIVE
        self.current_signal = "green"
        self.last_updated = datetime.now()
        return True
    
    def deactivate(self) -> bool:
        """Deactivate traffic signal (set to blinking red)"""
        self.status = DeviceStatus.INACTIVE
        self.current_signal = "red"
        self.last_updated = datetime.now()
        return True
    
    def set_signal(self, signal: str) -> bool:
        """Set traffic signal state"""
        if signal in ["red", "yellow", "green"]:
            self.current_signal = signal
            self.status = DeviceStatus.ACTIVE
            self.last_updated = datetime.now()
            return True
        return False
    
    def get_status_info(self) -> dict:
        """Get traffic signal status"""
        info = self.to_dict()
        info.update({
            'current_signal': self.current_signal,
            'cycle_duration': self.cycle_duration
        })
        return info


@dataclass
class SecurityCamera(Device):
    """Security camera device with recording capabilities"""
    recording: bool = False
    motion_detection: bool = True
    resolution: str = "1080p"
    
    def __post_init__(self):
        super().__post_init__()
        self.device_type = DeviceType.SECURITY_CAMERA
    
    def activate(self) -> bool:
        """Start recording"""
        self.status = DeviceStatus.ACTIVE
        self.recording = True
        self.last_updated = datetime.now()
        return True
    
    def deactivate(self) -> bool:
        """Stop recording"""
        self.status = DeviceStatus.INACTIVE
        self.recording = False
        self.last_updated = datetime.now()
        return True
    
    def toggle_motion_detection(self) -> bool:
        """Toggle motion detection"""
        self.motion_detection = not self.motion_detection
        self.last_updated = datetime.now()
        return self.motion_detection
    
    def get_status_info(self) -> dict:
        """Get camera status"""
        info = self.to_dict()
        info.update({
            'recording': self.recording,
            'motion_detection': self.motion_detection,
            'resolution': self.resolution
        })
        return info
