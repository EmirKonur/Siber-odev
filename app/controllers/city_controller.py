"""
CityController - Singleton Pattern Implementation
Central controller for all city infrastructure management
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import threading


class CityController:
    """
    Singleton class that manages all city infrastructure.
    Implements the Singleton pattern to ensure only one instance
    controls the entire city infrastructure.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._devices: Dict[str, Any] = {}
        self._command_history: List[dict] = []
        self._routines: List[dict] = []
        self._stats = {
            'total_commands': 0,
            'active_devices': 0,
            'last_routine': None,
            'uptime_start': datetime.now()
        }
        self._initialized = True
    
    @classmethod
    def get_instance(cls) -> 'CityController':
        """Get the singleton instance of CityController"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (for testing)"""
        cls._instance = None
    
    # ==================== Device Management ====================
    
    def register_device(self, device) -> bool:
        """Register a new device with the city controller"""
        device_id = device.device_id
        if device_id not in self._devices:
            self._devices[device_id] = device
            self._update_active_count()
            return True
        return False
    
    def unregister_device(self, device_id: str) -> bool:
        """Unregister a device from the city controller"""
        if device_id in self._devices:
            del self._devices[device_id]
            self._update_active_count()
            return True
        return False
    
    def get_device(self, device_id: str) -> Optional[Any]:
        """Get a specific device by ID"""
        return self._devices.get(device_id)
    
    def get_all_devices(self) -> List[dict]:
        """Get all registered devices as dictionaries"""
        return [device.to_dict() for device in self._devices.values()]
    
    def get_devices_by_type(self, device_type: str) -> List[dict]:
        """Get all devices of a specific type"""
        return [
            device.to_dict() 
            for device in self._devices.values() 
            if device.device_type.value == device_type
        ]
    
    def _update_active_count(self) -> None:
        """Update the count of active devices"""
        self._stats['active_devices'] = sum(
            1 for d in self._devices.values() 
            if d.status.value == 'active'
        )
    
    # ==================== Command Execution ====================
    
    def execute_command(self, command) -> dict:
        """
        Execute a command on the city infrastructure.
        Uses Command pattern for operations.
        """
        result = command.execute()
        
        # Log command execution
        self._command_history.append({
            'command': command.__class__.__name__,
            'timestamp': datetime.now().isoformat(),
            'success': result.get('success', False)
        })
        
        self._stats['total_commands'] += 1
        self._update_active_count()
        
        return result
    
    def undo_last_command(self) -> Optional[dict]:
        """Undo the last executed command if possible"""
        if self._command_history:
            last = self._command_history[-1]
            # Implementation would depend on command supporting undo
            return {'message': f"Attempted to undo {last['command']}"}
        return None
    
    def get_command_history(self, limit: int = 10) -> List[dict]:
        """Get recent command history"""
        return self._command_history[-limit:]
    
    # ==================== Device Control ====================
    
    def activate_device(self, device_id: str) -> dict:
        """Activate a specific device"""
        device = self.get_device(device_id)
        if device:
            success = device.activate()
            self._update_active_count()
            return {'success': success, 'device_id': device_id, 'action': 'activate'}
        return {'success': False, 'error': f'Device {device_id} not found'}
    
    def deactivate_device(self, device_id: str) -> dict:
        """Deactivate a specific device"""
        device = self.get_device(device_id)
        if device:
            success = device.deactivate()
            self._update_active_count()
            return {'success': success, 'device_id': device_id, 'action': 'deactivate'}
        return {'success': False, 'error': f'Device {device_id} not found'}
    
    def set_traffic_signal(self, device_id: str, signal: str) -> dict:
        """Set a traffic signal state"""
        device = self.get_device(device_id)
        if device and hasattr(device, 'set_signal'):
            success = device.set_signal(signal)
            return {'success': success, 'device_id': device_id, 'signal': signal}
        return {'success': False, 'error': f'Traffic signal {device_id} not found'}
    
    def set_light_brightness(self, device_id: str, brightness: int) -> dict:
        """Set street light brightness"""
        device = self.get_device(device_id)
        if device and hasattr(device, 'set_brightness'):
            success = device.set_brightness(brightness)
            return {'success': success, 'device_id': device_id, 'brightness': brightness}
        return {'success': False, 'error': f'Street light {device_id} not found'}
    
    # ==================== Routine Management ====================
    
    def register_routine(self, routine: dict) -> bool:
        """Register a daily routine"""
        self._routines.append(routine)
        return True
    
    def execute_routine(self, routine_name: str) -> dict:
        """Execute a registered routine"""
        self._stats['last_routine'] = {
            'name': routine_name,
            'executed_at': datetime.now().isoformat()
        }
        return {'success': True, 'routine': routine_name}
    
    # ==================== Statistics ====================
    
    def get_system_stats(self) -> dict:
        """Get system statistics"""
        uptime = datetime.now() - self._stats['uptime_start']
        return {
            'total_devices': len(self._devices),
            'active_devices': self._stats['active_devices'],
            'total_commands_executed': self._stats['total_commands'],
            'last_routine': self._stats['last_routine'],
            'uptime_seconds': uptime.total_seconds(),
            'uptime_formatted': str(uptime).split('.')[0]
        }
