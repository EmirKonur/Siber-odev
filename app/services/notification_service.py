"""
NotificationService - Observer Pattern Implementation
Manages system notifications and alerts
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum


class NotificationType(Enum):
    """Types of notifications"""
    INFO = "info"
    WARNING = "warning"
    SECURITY = "security"
    TRANSACTION = "transaction"
    EMERGENCY = "emergency"


class Observer(ABC):
    """
    Abstract Observer interface.
    Observers receive notifications from the NotificationService.
    """
    
    @abstractmethod
    def update(self, notification: dict) -> None:
        """Receive and process a notification"""
        pass
    
    @abstractmethod
    def get_type(self) -> str:
        """Get the observer type"""
        pass


class SecurityObserver(Observer):
    """Observer for security-related notifications"""
    
    def __init__(self):
        self._alerts: List[dict] = []
    
    def update(self, notification: dict) -> None:
        """Process security notification"""
        if notification.get('type') in ['security', 'emergency']:
            self._alerts.append({
                **notification,
                'processed_at': datetime.now().isoformat(),
                'status': 'received'
            })
            # In production, this would trigger alerts to authorities
            print(f"[SECURITY ALERT] {notification.get('message')}")
    
    def get_type(self) -> str:
        return "security"
    
    def get_alerts(self) -> List[dict]:
        return self._alerts


class TransactionObserver(Observer):
    """Observer for transaction notifications"""
    
    def __init__(self):
        self._notifications: List[dict] = []
    
    def update(self, notification: dict) -> None:
        """Process transaction notification"""
        if notification.get('type') == 'transaction':
            self._notifications.append({
                **notification,
                'processed_at': datetime.now().isoformat()
            })
            print(f"[TRANSACTION] {notification.get('message')}")
    
    def get_type(self) -> str:
        return "transaction"


class EmergencyObserver(Observer):
    """Observer for emergency alerts - notifies public safety authorities"""
    
    def __init__(self):
        self._emergencies: List[dict] = []
    
    def update(self, notification: dict) -> None:
        """Process emergency notification"""
        if notification.get('type') == 'emergency':
            emergency = {
                **notification,
                'escalated': True,
                'escalated_at': datetime.now().isoformat()
            }
            self._emergencies.append(emergency)
            # In production, this would notify emergency services
            print(f"[EMERGENCY] Escalating: {notification.get('message')}")
    
    def get_type(self) -> str:
        return "emergency"


class NotificationService:
    """
    Subject in the Observer pattern.
    Manages observers and distributes notifications.
    """
    
    def __init__(self):
        self._observers: List[Observer] = []
        self._notifications: List[dict] = []
        self._security_alerts: List[dict] = []
    
    def attach(self, observer: Observer) -> None:
        """Attach an observer to receive notifications"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Detach an observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, message: str, notification_type: str = "info", **kwargs) -> dict:
        """
        Create and distribute a notification to all observers.
        """
        notification = {
            'id': len(self._notifications) + 1,
            'message': message,
            'type': notification_type,
            'timestamp': datetime.now().isoformat(),
            **kwargs
        }
        
        self._notifications.append(notification)
        
        # Track security alerts separately
        if notification_type in ['security', 'emergency']:
            self._security_alerts.append(notification)
        
        # Notify all observers
        for observer in self._observers:
            try:
                observer.update(notification)
            except Exception as e:
                print(f"Error notifying observer: {e}")
        
        return notification
    
    def notify_security(self, message: str, severity: str = "medium", **kwargs) -> dict:
        """Send a security notification"""
        return self.notify(
            message=message,
            notification_type="security",
            severity=severity,
            **kwargs
        )
    
    def notify_emergency(self, message: str, location: str = "", **kwargs) -> dict:
        """Send an emergency notification"""
        return self.notify(
            message=message,
            notification_type="emergency",
            location=location,
            priority="critical",
            **kwargs
        )
    
    def notify_transaction(self, message: str, amount: float = 0, **kwargs) -> dict:
        """Send a transaction notification"""
        return self.notify(
            message=message,
            notification_type="transaction",
            amount=amount,
            **kwargs
        )
    
    def get_recent_notifications(self, limit: int = 20) -> List[dict]:
        """Get recent notifications"""
        return sorted(
            self._notifications,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limit]
    
    def get_security_alerts(self, limit: int = 10) -> List[dict]:
        """Get security alerts"""
        return sorted(
            self._security_alerts,
            key=lambda x: x['timestamp'],
            reverse=True
        )[:limit]
    
    def get_notifications_by_type(self, notification_type: str) -> List[dict]:
        """Get notifications filtered by type"""
        return [n for n in self._notifications if n['type'] == notification_type]
    
    def clear_old_notifications(self, keep_count: int = 100) -> int:
        """Clear old notifications, keeping the most recent ones"""
        if len(self._notifications) > keep_count:
            removed = len(self._notifications) - keep_count
            self._notifications = self._notifications[-keep_count:]
            return removed
        return 0
