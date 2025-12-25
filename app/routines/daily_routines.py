"""
Daily Routines - Template Method Pattern Implementation
Defines skeleton of daily automation routines with customizable steps
"""
from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime


class DailyRoutineTemplate(ABC):
    """
    Abstract class implementing the Template Method pattern.
    Defines the skeleton of daily automation routines.
    Subclasses override specific steps while the overall algorithm remains the same.
    """
    
    def __init__(self, city_controller):
        self._controller = city_controller
        self._log: List[Dict] = []
    
    def execute(self) -> dict:
        """
        Template method that defines the skeleton of the routine.
        Subclasses cannot override this method.
        """
        self._log = []
        
        # Template algorithm
        self._log_step("Starting routine")
        
        try:
            # Step 1: Prepare (hook - can be overridden)
            self.prepare()
            self._log_step("Preparation complete")
            
            # Step 2: Execute main operations (abstract - must be overridden)
            self.execute_main_operations()
            self._log_step("Main operations complete")
            
            # Step 3: Verify execution (hook - can be overridden)
            verification = self.verify()
            self._log_step(f"Verification: {verification}")
            
            # Step 4: Cleanup (hook - can be overridden)
            self.cleanup()
            self._log_step("Cleanup complete")
            
            # Step 5: Notify completion
            self.notify_completion()
            self._log_step("Routine completed successfully")
            
            return {
                'success': True,
                'routine': self.get_name(),
                'executed_at': datetime.now().isoformat(),
                'log': self._log
            }
            
        except Exception as e:
            self._log_step(f"Error: {str(e)}")
            return {
                'success': False,
                'routine': self.get_name(),
                'error': str(e),
                'log': self._log
            }
    
    def _log_step(self, message: str) -> None:
        """Log a step in the routine"""
        self._log.append({
            'timestamp': datetime.now().isoformat(),
            'message': message
        })
    
    # ==================== Template Steps ====================
    
    def prepare(self) -> None:
        """
        Hook method for preparation.
        Can be overridden by subclasses.
        """
        pass
    
    @abstractmethod
    def execute_main_operations(self) -> None:
        """
        Abstract method that must be implemented by subclasses.
        Contains the main routine operations.
        """
        pass
    
    def verify(self) -> bool:
        """
        Hook method for verification.
        Can be overridden by subclasses.
        """
        return True
    
    def cleanup(self) -> None:
        """
        Hook method for cleanup.
        Can be overridden by subclasses.
        """
        pass
    
    def notify_completion(self) -> None:
        """
        Hook method for notification.
        Can be overridden by subclasses.
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Get the routine name"""
        pass


class SunriseRoutine(DailyRoutineTemplate):
    """
    Sunrise routine - executes at dawn.
    Turns off street lights,adjusts traffic patterns for morning rush.
    """
    
    def prepare(self) -> None:
        """Prepare for sunrise routine"""
        # Check current light status
        devices = self._controller.get_all_devices()
        self._active_lights = [
            d['device_id'] for d in devices 
            if d['type'] == 'StreetLight' and d['status'] == 'active'
        ]
    
    def execute_main_operations(self) -> None:
        """Turn off street lights at sunrise"""
        # Gradually dim and turn off all street lights
        for device_id in self._active_lights:
            device = self._controller.get_device(device_id)
            if device:
                # Gradually reduce brightness
                if hasattr(device, 'set_brightness'):
                    device.set_brightness(50)  # Dim first
                    device.set_brightness(25)
                    device.set_brightness(0)
                device.deactivate()
        
        # Adjust traffic signals for morning patterns
        traffic_signals = self._controller.get_devices_by_type('TrafficSignal')
        for signal in traffic_signals:
            device = self._controller.get_device(signal['device_id'])
            if device and hasattr(device, 'cycle_duration'):
                # Shorter cycles for morning rush
                device.cycle_duration = 45
    
    def verify(self) -> bool:
        """Verify all lights are off"""
        devices = self._controller.get_all_devices()
        lights_off = all(
            d['status'] == 'inactive' 
            for d in devices 
            if d['type'] == 'StreetLight'
        )
        return lights_off
    
    def notify_completion(self) -> None:
        """Log completion"""
        self._log_step(f"Deactivated {len(self._active_lights)} street lights")
    
    def get_name(self) -> str:
        return "Sunrise Routine"


class SunsetRoutine(DailyRoutineTemplate):
    """
    Sunset routine - executes at dusk.
    Turns on street lights, adjusts traffic patterns for evening.
    """
    
    def prepare(self) -> None:
        """Prepare for sunset routine"""
        devices = self._controller.get_all_devices()
        self._lights_to_activate = [
            d['device_id'] for d in devices 
            if d['type'] == 'StreetLight'
        ]
    
    def execute_main_operations(self) -> None:
        """Turn on street lights at sunset"""
        # Gradually turn on all street lights
        for device_id in self._lights_to_activate:
            device = self._controller.get_device(device_id)
            if device:
                device.activate()
                # Gradually increase brightness
                if hasattr(device, 'set_brightness'):
                    device.set_brightness(50)
                    device.set_brightness(75)
                    device.set_brightness(100)
        
        # Adjust traffic signals for evening patterns
        traffic_signals = self._controller.get_devices_by_type('TrafficSignal')
        for signal in traffic_signals:
            device = self._controller.get_device(signal['device_id'])
            if device and hasattr(device, 'cycle_duration'):
                # Longer cycles for evening
                device.cycle_duration = 60
    
    def verify(self) -> bool:
        """Verify all lights are on"""
        devices = self._controller.get_all_devices()
        lights_on = all(
            d['status'] == 'active' 
            for d in devices 
            if d['type'] == 'StreetLight'
        )
        return lights_on
    
    def notify_completion(self) -> None:
        """Log completion"""
        self._log_step(f"Activated {len(self._lights_to_activate)} street lights")
    
    def get_name(self) -> str:
        return "Sunset Routine"


class EnergyOptimizationRoutine(DailyRoutineTemplate):
    """
    Energy optimization routine.
    Analyzes usage patterns and adjusts devices for optimal energy consumption.
    """
    
    def prepare(self) -> None:
        """Analyze current energy usage"""
        self._devices = self._controller.get_all_devices()
        self._optimizations = []
    
    def execute_main_operations(self) -> None:
        """Optimize energy usage for all devices"""
        for device_data in self._devices:
            device = self._controller.get_device(device_data['device_id'])
            if not device:
                continue
            
            # Optimize street lights based on time
            if device_data['type'] == 'StreetLight':
                current_hour = datetime.now().hour
                if 1 <= current_hour <= 5:
                    # Reduce brightness during low-traffic hours
                    if hasattr(device, 'set_brightness'):
                        device.set_brightness(60)
                        self._optimizations.append(f"Dimmed {device_data['device_id']} to 60%")
    
    def verify(self) -> bool:
        """Verify optimizations applied"""
        return len(self._optimizations) > 0
    
    def notify_completion(self) -> None:
        """Log optimizations"""
        self._log_step(f"Applied {len(self._optimizations)} optimizations")
    
    def get_name(self) -> str:
        return "Energy Optimization Routine"
