"""
BankingController - Manages digital banking operations
Supports both fiat and cryptocurrency payments using Adapter pattern
"""
from typing import Dict, List, Optional
from datetime import datetime
from app.models.transaction import Transaction, TransactionType, TransactionStatus
from app.services.crypto_adapter import CryptoPaymentAdapter, BitcoinAdapter, EthereumAdapter


class BankingController:
    """
    Controller for handling all banking operations.
    Integrates with fiat and cryptocurrency payment systems.
    """
    
    def __init__(self):
        self._transactions: List[Transaction] = []
        self._balances: Dict[str, float] = {'R001': 1000.0}  # Sample balance
        self._crypto_adapters: Dict[str, CryptoPaymentAdapter] = {
            'bitcoin': BitcoinAdapter(),
            'ethereum': EthereumAdapter()
        }
        self._fee_rates = {
            'fiat': 0.01,      # 1% fee
            'bitcoin': 0.02,   # 2% fee
            'ethereum': 0.015  # 1.5% fee
        }
    
    def process_payment(
        self,
        resident_id: str,
        amount: float,
        currency: str,
        payment_type: str = 'fiat',
        description: str = ''
    ) -> dict:
        """
        Process a payment transaction.
        Uses Adapter pattern for cryptocurrency payments.
        """
        # Determine transaction type
        if payment_type == 'bitcoin':
            tx_type = TransactionType.CRYPTO_BTC
        elif payment_type == 'ethereum':
            tx_type = TransactionType.CRYPTO_ETH
        else:
            tx_type = TransactionType.FIAT
        
        # Calculate fee
        fee_rate = self._fee_rates.get(payment_type, 0.01)
        fee = amount * fee_rate
        total = amount + fee
        
        # Check balance
        current_balance = self._balances.get(resident_id, 0)
        if current_balance < total:
            return {
                'success': False,
                'error': 'Insufficient funds',
                'balance': current_balance,
                'required': total
            }
        
        # Create transaction
        transaction = Transaction(
            resident_id=resident_id,
            amount=amount,
            currency=currency,
            description=description,
            transaction_type=tx_type,
            fee=fee
        )
        
        # Process based on payment type
        if payment_type in ['bitcoin', 'ethereum']:
            adapter = self._crypto_adapters.get(payment_type)
            if adapter:
                result = adapter.process_payment(amount, currency)
                if not result['success']:
                    transaction.fail(result.get('error', 'Crypto payment failed'))
                    self._transactions.append(transaction)
                    return {'success': False, 'error': result.get('error')}
        
        # Deduct balance and complete transaction
        self._balances[resident_id] = current_balance - total
        transaction.complete()
        self._transactions.append(transaction)
        
        return {
            'success': True,
            'transaction': transaction.to_dict(),
            'new_balance': self._balances[resident_id]
        }
    
    def get_balance(self, resident_id: str) -> dict:
        """Get resident's current balance"""
        balance = self._balances.get(resident_id, 0)
        return {
            'resident_id': resident_id,
            'balance': balance,
            'currency': 'USD'
        }
    
    def add_funds(self, resident_id: str, amount: float) -> dict:
        """Add funds to resident's account"""
        current = self._balances.get(resident_id, 0)
        self._balances[resident_id] = current + amount
        return {
            'success': True,
            'new_balance': self._balances[resident_id]
        }
    
    def get_recent_transactions(self, limit: int = 10) -> List[dict]:
        """Get recent transactions"""
        sorted_tx = sorted(
            self._transactions,
            key=lambda x: x.timestamp,
            reverse=True
        )
        return [tx.to_dict() for tx in sorted_tx[:limit]]
    
    def get_transactions_by_resident(self, resident_id: str) -> List[dict]:
        """Get all transactions for a specific resident"""
        return [
            tx.to_dict() 
            for tx in self._transactions 
            if tx.resident_id == resident_id
        ]
    
    def refund_transaction(self, transaction_id: str) -> dict:
        """Process a refund for a transaction"""
        for tx in self._transactions:
            if tx.transaction_id == transaction_id:
                if tx.refund():
                    # Restore balance
                    self._balances[tx.resident_id] = (
                        self._balances.get(tx.resident_id, 0) + tx.get_total()
                    )
                    return {
                        'success': True,
                        'refunded_amount': tx.get_total()
                    }
                return {'success': False, 'error': 'Transaction cannot be refunded'}
        return {'success': False, 'error': 'Transaction not found'}
    
    def get_transaction_stats(self) -> dict:
        """Get transaction statistics"""
        total_amount = sum(tx.amount for tx in self._transactions if tx.status == TransactionStatus.COMPLETED)
        total_fees = sum(tx.fee for tx in self._transactions if tx.status == TransactionStatus.COMPLETED)
        
        return {
            'total_transactions': len(self._transactions),
            'completed': sum(1 for tx in self._transactions if tx.status == TransactionStatus.COMPLETED),
            'failed': sum(1 for tx in self._transactions if tx.status == TransactionStatus.FAILED),
            'total_amount': total_amount,
            'total_fees': total_fees
        }
