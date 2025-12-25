"""
Infrastructure Commands - Command Pattern Implementation
Encapsulates operations as objects for execution, undo, and logging
"""
from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime


class Command(ABC):
    """
    Abstract Command interface.
    Implements the Command pattern for infrastructure operations.
    """
    
    @abstractmethod
    def execute(self) -> dict:
        """Execute the command"""
        pass
    
    @abstractmethod
    def undo(self) -> dict:
        """Undo the command if possible"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get a description of the command"""
        pass


class LightOnCommand(Command):
    """Command to turn on a street light"""
    
    def __init__(self, controller, device_id: str, brightness: int = 100):
        self._controller = controller
        self._device_id = device_id
        self._brightness = brightness
        self._previous_state = None
    
    def execute(self) -> dict:
        """Turn on the light"""
        device = self._controller.get_device(self._device_id)
        if device:
            # Store previous state for undo
            self._previous_state = {
                'status': device.status,
                'brightness': getattr(device, 'brightness', 0)
            }
            result = device.activate()
            if hasattr(device, 'set_brightness'):
                device.set_brightness(self._brightness)
            return {
                'success': result,
                'device_id': self._device_id,
                'action': 'light_on',
                'brightness': self._brightness,
                'timestamp': datetime.now().isoformat()
            }
        return {'success': False, 'error': f'Device {self._device_id} not found'}
    
    def undo(self) -> dict:
        """Restore previous light state"""
        if self._previous_state:
            device = self._controller.get_device(self._device_id)
            if device:
                device.deactivate()
                return {'success': True, 'action': 'undo_light_on'}
        return {'success': False, 'error': 'No previous state to restore'}
    
    def get_description(self) -> str:
        return f"Turn on light {self._device_id} at {self._brightness}% brightness"


class LightOffCommand(Command):
    """Command to turn off a street light"""
    
    def __init__(self, controller, device_id: str):
        self._controller = controller
        self._device_id = device_id
        self._previous_brightness = None
    
    def execute(self) -> dict:
        """Turn off the light"""
        device = self._controller.get_device(self._device_id)
        if device:
            self._previous_brightness = getattr(device, 'brightness', 100)
            result = device.deactivate()
            return {
                'success': result,
                'device_id': self._device_id,
                'action': 'light_off',
                'timestamp': datetime.now().isoformat()
            }
        return {'success': False, 'error': f'Device {self._device_id} not found'}
    
    def undo(self) -> dict:
        """Restore previous light state"""
        device = self._controller.get_device(self._device_id)
        if device and self._previous_brightness:
            device.activate()
            if hasattr(device, 'set_brightness'):
                device.set_brightness(self._previous_brightness)
            return {'success': True, 'action': 'undo_light_off'}
        return {'success': False, 'error': 'Cannot undo'}
    
    def get_description(self) -> str:
        return f"Turn off light {self._device_id}"


class TrafficGreenCommand(Command):
    """Command to set traffic signal to green"""
    
    def __init__(self, controller, device_id: str):
        self._controller = controller
        self._device_id = device_id
        self._previous_signal = None
    
    def execute(self) -> dict:
        """Set traffic signal to green"""
        device = self._controller.get_device(self._device_id)
        if device and hasattr(device, 'set_signal'):
            self._previous_signal = getattr(device, 'current_signal', 'red')
            result = device.set_signal('green')
            return {
                'success': result,
                'device_id': self._device_id,
                'action': 'traffic_green',
                'signal': 'green',
                'timestamp': datetime.now().isoformat()
            }
        return {'success': False, 'error': f'Traffic signal {self._device_id} not found'}
    
    def undo(self) -> dict:
        """Restore previous signal state"""
        if self._previous_signal:
            device = self._controller.get_device(self._device_id)
            if device and hasattr(device, 'set_signal'):
                device.set_signal(self._previous_signal)
                return {'success': True, 'action': 'undo_traffic_green'}
        return {'success': False, 'error': 'Cannot undo'}
    
    def get_description(self) -> str:
        return f"Set traffic signal {self._device_id} to green"


class TrafficRedCommand(Command):
    """Command to set traffic signal to red"""
    
    def __init__(self, controller, device_id: str):
        self._controller = controller
        self._device_id = device_id
        self._previous_signal = None
    
    def execute(self) -> dict:
        """Set traffic signal to red"""
        device = self._controller.get_device(self._device_id)
        if device and hasattr(device, 'set_signal'):
            self._previous_signal = getattr(device, 'current_signal', 'green')
            result = device.set_signal('red')
            return {
                'success': result,
                'device_id': self._device_id,
                'action': 'traffic_red',
                'signal': 'red',
                'timestamp': datetime.now().isoformat()
            }
        return {'success': False, 'error': f'Traffic signal {self._device_id} not found'}
    
    def undo(self) -> dict:
        """Restore previous signal state"""
        if self._previous_signal:
            device = self._controller.get_device(self._device_id)
            if device and hasattr(device, 'set_signal'):
                device.set_signal(self._previous_signal)
                return {'success': True, 'action': 'undo_traffic_red'}
        return {'success': False, 'error': 'Cannot undo'}
    
    def get_description(self) -> str:
        return f"Set traffic signal {self._device_id} to red"


class ProcessPaymentCommand(Command):
    """Command to process a payment"""
    
    def __init__(self, banking_controller, resident_id: str, amount: float, 
                 currency: str = 'USD', payment_type: str = 'fiat', 
                 description: str = ''):
        self._banking = banking_controller
        self._resident_id = resident_id
        self._amount = amount
        self._currency = currency
        self._payment_type = payment_type
        self._description = description
        self._transaction_id = None
    
    def execute(self) -> dict:
        """Process the payment"""
        result = self._banking.process_payment(
            resident_id=self._resident_id,
            amount=self._amount,
            currency=self._currency,
            payment_type=self._payment_type,
            description=self._description
        )
        
        if result.get('success'):
            self._transaction_id = result.get('transaction', {}).get('transaction_id')
        
        return result
    
    def undo(self) -> dict:
        """Refund the payment"""
        if self._transaction_id:
            return self._banking.refund_transaction(self._transaction_id)
        return {'success': False, 'error': 'No transaction to refund'}
    
    def get_description(self) -> str:
        return f"Process {self._payment_type} payment of {self._amount} {self._currency}"


class CommandInvoker:
    """
    Invoker class that executes and manages commands.
    Maintains command history for undo operations.
    """
    
    def __init__(self):
        self._history: list = []
        self._undo_stack: list = []
    
    def execute(self, command: Command) -> dict:
        """Execute a command and add to history"""
        result = command.execute()
        self._history.append({
            'command': command,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        self._undo_stack.append(command)
        return result
    
    def undo(self) -> Optional[dict]:
        """Undo the last command"""
        if self._undo_stack:
            command = self._undo_stack.pop()
            return command.undo()
        return None
    
    def get_history(self, limit: int = 10) -> list:
        """Get command execution history"""
        return [
            {
                'command': h['command'].get_description(),
                'success': h['result'].get('success', False),
                'timestamp': h['timestamp']
            }
            for h in self._history[-limit:]
        ]
