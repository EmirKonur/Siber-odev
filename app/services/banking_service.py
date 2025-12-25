"""
BankingService - Core banking operations
"""
from typing import Dict, List, Optional
from datetime import datetime


class BankingService:
    """
    Service layer for banking operations.
    Provides high-level banking functionality.
    """
    
    def __init__(self):
        self._accounts: Dict[str, dict] = {}
        self._pending_transactions: List[dict] = []
    
    def create_account(self, resident_id: str, initial_balance: float = 0) -> dict:
        """Create a new account for a resident"""
        if resident_id in self._accounts:
            return {'success': False, 'error': 'Account already exists'}
        
        self._accounts[resident_id] = {
            'resident_id': resident_id,
            'balance': initial_balance,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        return {
            'success': True,
            'account': self._accounts[resident_id]
        }
    
    def get_account(self, resident_id: str) -> Optional[dict]:
        """Get account details"""
        return self._accounts.get(resident_id)
    
    def deposit(self, resident_id: str, amount: float) -> dict:
        """Deposit funds into an account"""
        account = self._accounts.get(resident_id)
        if not account:
            return {'success': False, 'error': 'Account not found'}
        
        if amount <= 0:
            return {'success': False, 'error': 'Invalid amount'}
        
        account['balance'] += amount
        return {
            'success': True,
            'new_balance': account['balance']
        }
    
    def withdraw(self, resident_id: str, amount: float) -> dict:
        """Withdraw funds from an account"""
        account = self._accounts.get(resident_id)
        if not account:
            return {'success': False, 'error': 'Account not found'}
        
        if amount <= 0:
            return {'success': False, 'error': 'Invalid amount'}
        
        if account['balance'] < amount:
            return {'success': False, 'error': 'Insufficient funds'}
        
        account['balance'] -= amount
        return {
            'success': True,
            'new_balance': account['balance']
        }
    
    def transfer(self, from_id: str, to_id: str, amount: float) -> dict:
        """Transfer funds between accounts"""
        from_account = self._accounts.get(from_id)
        to_account = self._accounts.get(to_id)
        
        if not from_account or not to_account:
            return {'success': False, 'error': 'Account not found'}
        
        if from_account['balance'] < amount:
            return {'success': False, 'error': 'Insufficient funds'}
        
        from_account['balance'] -= amount
        to_account['balance'] += amount
        
        return {
            'success': True,
            'from_balance': from_account['balance'],
            'to_balance': to_account['balance']
        }
