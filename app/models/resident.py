"""
Resident Model - Represents city residents who interact with the system
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import uuid


@dataclass
class Resident:
    """
    Represents a resident of the smart city.
    Residents can control home devices, view city services,
    receive security alerts, and pay for services.
    """
    resident_id: str
    name: str
    email: str
    role: str = "resident"  # resident, admin, authority
    registered_devices: List[str] = field(default_factory=list)
    balance: float = 1000.0
    mfa_enabled: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.resident_id:
            self.resident_id = str(uuid.uuid4())
    
    def add_device(self, device_id: str) -> bool:
        """Register a device to this resident"""
        if device_id not in self.registered_devices:
            self.registered_devices.append(device_id)
            return True
        return False
    
    def remove_device(self, device_id: str) -> bool:
        """Unregister a device from this resident"""
        if device_id in self.registered_devices:
            self.registered_devices.remove(device_id)
            return True
        return False
    
    def update_balance(self, amount: float) -> bool:
        """Update resident's balance"""
        new_balance = self.balance + amount
        if new_balance >= 0:
            self.balance = new_balance
            return True
        return False
    
    def enable_mfa(self) -> None:
        """Enable multi-factor authentication"""
        self.mfa_enabled = True
    
    def has_permission(self, permission: str) -> bool:
        """Check if resident has a specific permission based on role"""
        permissions = {
            'resident': ['view_services', 'control_home_devices', 'make_payments'],
            'admin': ['view_services', 'control_home_devices', 'make_payments', 
                     'control_infrastructure', 'view_analytics', 'manage_users'],
            'authority': ['view_services', 'receive_alerts', 'view_analytics']
        }
        return permission in permissions.get(self.role, [])
    
    def to_dict(self) -> dict:
        """Convert resident to dictionary"""
        return {
            'resident_id': self.resident_id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'registered_devices': self.registered_devices,
            'balance': self.balance,
            'mfa_enabled': self.mfa_enabled,
            'created_at': self.created_at.isoformat()
        }
