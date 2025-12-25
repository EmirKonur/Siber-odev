"""
CryptoPaymentAdapter - Adapter Pattern Implementation
Provides unified interface for multiple cryptocurrency payment systems
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime
import hashlib
import random


class CryptoPaymentAdapter(ABC):
    """
    Abstract adapter interface for cryptocurrency payments.
    Implements the Adapter pattern to provide a unified interface
    for different cryptocurrency payment systems.
    """
    
    @abstractmethod
    def process_payment(self, amount: float, currency: str) -> dict:
        """Process a cryptocurrency payment"""
        pass
    
    @abstractmethod
    def get_exchange_rate(self, fiat_currency: str) -> float:
        """Get current exchange rate to fiat currency"""
        pass
    
    @abstractmethod
    def validate_address(self, address: str) -> bool:
        """Validate a cryptocurrency wallet address"""
        pass
    
    @abstractmethod
    def get_network_fee(self) -> float:
        """Get current network transaction fee"""
        pass


class BitcoinAdapter(CryptoPaymentAdapter):
    """
    Adapter for Bitcoin payments.
    Wraps Bitcoin-specific operations into the common interface.
    """
    
    def __init__(self):
        self._name = "Bitcoin"
        self._symbol = "BTC"
        # Simulated exchange rates (in production, fetch from API)
        self._exchange_rate = 43500.00  # USD per BTC
        self._network_fee = 0.0001  # BTC
    
    def process_payment(self, amount: float, currency: str) -> dict:
        """Process Bitcoin payment"""
        try:
            # Convert amount to BTC if needed
            btc_amount = amount / self._exchange_rate if currency == 'USD' else amount
            
            # Generate mock transaction hash
            tx_data = f"{amount}{currency}{datetime.now().isoformat()}{random.random()}"
            tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
            
            return {
                'success': True,
                'crypto': self._symbol,
                'amount_btc': btc_amount,
                'amount_fiat': amount if currency == 'USD' else btc_amount * self._exchange_rate,
                'tx_hash': tx_hash,
                'network_fee': self._network_fee,
                'confirmations_required': 3,
                'estimated_confirmation_time': '30 minutes'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'crypto': self._symbol
            }
    
    def get_exchange_rate(self, fiat_currency: str = 'USD') -> float:
        """Get BTC exchange rate"""
        # In production, fetch from cryptocurrency API
        rates = {
            'USD': self._exchange_rate,
            'EUR': self._exchange_rate * 0.92,
            'GBP': self._exchange_rate * 0.79,
            'TRY': self._exchange_rate * 29.5
        }
        return rates.get(fiat_currency, self._exchange_rate)
    
    def validate_address(self, address: str) -> bool:
        """Validate Bitcoin address format"""
        # Simplified validation (production would use proper validation)
        if not address:
            return False
        # BTC addresses start with 1, 3, or bc1
        return (
            len(address) >= 26 and 
            len(address) <= 62 and
            (address.startswith('1') or address.startswith('3') or address.startswith('bc1'))
        )
    
    def get_network_fee(self) -> float:
        """Get current Bitcoin network fee"""
        return self._network_fee


class EthereumAdapter(CryptoPaymentAdapter):
    """
    Adapter for Ethereum payments.
    Wraps Ethereum-specific operations into the common interface.
    """
    
    def __init__(self):
        self._name = "Ethereum"
        self._symbol = "ETH"
        # Simulated exchange rates
        self._exchange_rate = 2250.00  # USD per ETH
        self._gas_price = 25  # Gwei
        self._gas_limit = 21000
    
    def process_payment(self, amount: float, currency: str) -> dict:
        """Process Ethereum payment"""
        try:
            # Convert amount to ETH if needed
            eth_amount = amount / self._exchange_rate if currency == 'USD' else amount
            
            # Calculate gas fee
            gas_fee = (self._gas_price * self._gas_limit) / 1e9  # Convert Gwei to ETH
            
            # Generate mock transaction hash
            tx_data = f"{amount}{currency}{datetime.now().isoformat()}{random.random()}"
            tx_hash = "0x" + hashlib.sha256(tx_data.encode()).hexdigest()
            
            return {
                'success': True,
                'crypto': self._symbol,
                'amount_eth': eth_amount,
                'amount_fiat': amount if currency == 'USD' else eth_amount * self._exchange_rate,
                'tx_hash': tx_hash,
                'gas_fee': gas_fee,
                'gas_price_gwei': self._gas_price,
                'confirmations_required': 12,
                'estimated_confirmation_time': '5 minutes'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'crypto': self._symbol
            }
    
    def get_exchange_rate(self, fiat_currency: str = 'USD') -> float:
        """Get ETH exchange rate"""
        rates = {
            'USD': self._exchange_rate,
            'EUR': self._exchange_rate * 0.92,
            'GBP': self._exchange_rate * 0.79,
            'TRY': self._exchange_rate * 29.5
        }
        return rates.get(fiat_currency, self._exchange_rate)
    
    def validate_address(self, address: str) -> bool:
        """Validate Ethereum address format"""
        # ETH addresses are 42 characters starting with 0x
        if not address:
            return False
        return len(address) == 42 and address.startswith('0x')
    
    def get_network_fee(self) -> float:
        """Get current Ethereum gas fee in ETH"""
        return (self._gas_price * self._gas_limit) / 1e9


class CryptoPaymentFactory:
    """Factory for creating cryptocurrency adapters"""
    
    @staticmethod
    def get_adapter(crypto_type: str) -> CryptoPaymentAdapter:
        """Get the appropriate adapter for a cryptocurrency"""
        adapters = {
            'bitcoin': BitcoinAdapter,
            'btc': BitcoinAdapter,
            'ethereum': EthereumAdapter,
            'eth': EthereumAdapter
        }
        
        adapter_class = adapters.get(crypto_type.lower())
        if adapter_class:
            return adapter_class()
        raise ValueError(f"Unsupported cryptocurrency: {crypto_type}")
