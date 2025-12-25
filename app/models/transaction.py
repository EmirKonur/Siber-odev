"""
Transaction Model - Represents financial transactions in the system
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid
import hashlib


class TransactionType(Enum):
    """Types of transactions"""
    FIAT = "fiat"
    CRYPTO_BTC = "bitcoin"
    CRYPTO_ETH = "ethereum"


class TransactionStatus(Enum):
    """Transaction status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class Transaction:
    """
    Represents a financial transaction for city services.
    Supports both fiat and cryptocurrency payments.
    """
    resident_id: str
    amount: float
    currency: str
    description: str
    transaction_id: str = ""
    transaction_type: TransactionType = TransactionType.FIAT
    status: TransactionStatus = TransactionStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.now)
    hash: str = ""
    fee: float = 0.0
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.transaction_id:
            self.transaction_id = str(uuid.uuid4())
        if not self.hash:
            self.hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        """Generate a unique hash for the transaction"""
        data = f"{self.transaction_id}{self.resident_id}{self.amount}{self.timestamp.isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def complete(self) -> bool:
        """Mark transaction as completed"""
        self.status = TransactionStatus.COMPLETED
        return True
    
    def fail(self, reason: str = "") -> bool:
        """Mark transaction as failed"""
        self.status = TransactionStatus.FAILED
        self.metadata['failure_reason'] = reason
        return True
    
    def refund(self) -> bool:
        """Process a refund for this transaction"""
        if self.status == TransactionStatus.COMPLETED:
            self.status = TransactionStatus.REFUNDED
            return True
        return False
    
    def get_total(self) -> float:
        """Get total amount including fees"""
        return self.amount + self.fee
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary"""
        return {
            'transaction_id': self.transaction_id,
            'resident_id': self.resident_id,
            'amount': self.amount,
            'currency': self.currency,
            'description': self.description,
            'type': self.transaction_type.value,
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat(),
            'hash': self.hash,
            'fee': self.fee,
            'total': self.get_total()
        }
