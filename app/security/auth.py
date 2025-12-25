"""
Authentication Service - Security Module
Multi-factor authentication and role-based access control
"""
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import secrets
import hmac


class UserRole(Enum):
    """User roles for access control"""
    RESIDENT = "resident"
    ADMIN = "admin"
    OPERATOR = "operator"
    AUTHORITY = "authority"


class AuthService:
    """
    Authentication service providing:
    - Multi-factor authentication (MFA)
    - Role-based access control (RBAC)
    - Session management
    - Password hashing
    """
    
    def __init__(self):
        self._users: Dict[str, dict] = {}
        self._sessions: Dict[str, dict] = {}
        self._mfa_codes: Dict[str, str] = {}
        self._failed_attempts: Dict[str, int] = {}
        self._lockout_time: Dict[str, datetime] = {}
        
        # Default permissions per role
        self._role_permissions = {
            UserRole.RESIDENT: [
                'view_dashboard', 'control_home_devices', 
                'view_services', 'make_payments'
            ],
            UserRole.ADMIN: [
                'view_dashboard', 'control_home_devices', 'view_services',
                'make_payments', 'control_infrastructure', 'view_analytics',
                'manage_users', 'manage_devices', 'execute_routines'
            ],
            UserRole.OPERATOR: [
                'view_dashboard', 'control_infrastructure', 
                'view_analytics', 'execute_routines'
            ],
            UserRole.AUTHORITY: [
                'view_dashboard', 'receive_alerts', 
                'view_analytics', 'view_security_logs'
            ]
        }
        
        # Initialize sample user
        self._create_sample_users()
    
    def _create_sample_users(self) -> None:
        """Create sample users for demonstration"""
        self.register_user(
            user_id="R001",
            email="john@smartcity.com",
            password="SecurePass123!",
            role=UserRole.RESIDENT
        )
        self.register_user(
            user_id="A001",
            email="admin@smartcity.com",
            password="AdminPass123!",
            role=UserRole.ADMIN
        )
    
    def _hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Hash password using SHA-256 with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Multiple iterations for security
        hashed = password + salt
        for _ in range(10000):
            hashed = hashlib.sha256(hashed.encode()).hexdigest()
        
        return hashed, salt
    
    def _verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash"""
        computed_hash, _ = self._hash_password(password, salt)
        return hmac.compare_digest(computed_hash, stored_hash)
    
    def register_user(
        self, 
        user_id: str, 
        email: str, 
        password: str, 
        role: UserRole = UserRole.RESIDENT
    ) -> dict:
        """Register a new user"""
        if user_id in self._users:
            return {'success': False, 'error': 'User already exists'}
        
        password_hash, salt = self._hash_password(password)
        
        self._users[user_id] = {
            'user_id': user_id,
            'email': email,
            'password_hash': password_hash,
            'salt': salt,
            'role': role,
            'mfa_enabled': False,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        return {'success': True, 'user_id': user_id}
    
    def authenticate(self, user_id: str, password: str) -> dict:
        """
        Authenticate user with password.
        Returns MFA requirement if enabled.
        """
        # Check lockout
        if self._is_locked_out(user_id):
            return {
                'success': False,
                'error': 'Account locked due to too many failed attempts',
                'locked_until': self._lockout_time.get(user_id).isoformat()
            }
        
        user = self._users.get(user_id)
        if not user:
            return {'success': False, 'error': 'Invalid credentials'}
        
        if not self._verify_password(password, user['password_hash'], user['salt']):
            self._record_failed_attempt(user_id)
            return {'success': False, 'error': 'Invalid credentials'}
        
        # Reset failed attempts on success
        self._failed_attempts[user_id] = 0
        
        # Check if MFA is required
        if user['mfa_enabled']:
            mfa_code = self._generate_mfa_code(user_id)
            return {
                'success': True,
                'mfa_required': True,
                'message': 'MFA code sent to registered device'
            }
        
        # Create session
        session = self._create_session(user_id)
        user['last_login'] = datetime.now().isoformat()
        
        return {
            'success': True,
            'session_token': session['token'],
            'expires_at': session['expires_at'],
            'role': user['role'].value
        }
    
    def verify_mfa(self, user_id: str, code: str) -> dict:
        """Verify MFA code and complete authentication"""
        stored_code = self._mfa_codes.get(user_id)
        
        if not stored_code or stored_code != code:
            return {'success': False, 'error': 'Invalid MFA code'}
        
        # Clear used code
        del self._mfa_codes[user_id]
        
        # Create session
        session = self._create_session(user_id)
        user = self._users[user_id]
        user['last_login'] = datetime.now().isoformat()
        
        return {
            'success': True,
            'session_token': session['token'],
            'expires_at': session['expires_at']
        }
    
    def _generate_mfa_code(self, user_id: str) -> str:
        """Generate a 6-digit MFA code"""
        code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        self._mfa_codes[user_id] = code
        # In production, send this via SMS/email/authenticator app
        return code
    
    def _create_session(self, user_id: str) -> dict:
        """Create a new session for the user"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)
        
        self._sessions[token] = {
            'user_id': user_id,
            'token': token,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat()
        }
        
        return self._sessions[token]
    
    def validate_session(self, token: str) -> Optional[dict]:
        """Validate a session token"""
        session = self._sessions.get(token)
        if not session:
            return None
        
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.now() > expires_at:
            del self._sessions[token]
            return None
        
        return session
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has a specific permission"""
        user = self._users.get(user_id)
        if not user:
            return False
        
        role = user['role']
        permissions = self._role_permissions.get(role, [])
        return permission in permissions
    
    def enable_mfa(self, user_id: str) -> dict:
        """Enable MFA for a user"""
        user = self._users.get(user_id)
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        user['mfa_enabled'] = True
        return {'success': True, 'message': 'MFA enabled'}
    
    def logout(self, token: str) -> dict:
        """Logout and invalidate session"""
        if token in self._sessions:
            del self._sessions[token]
            return {'success': True}
        return {'success': False, 'error': 'Session not found'}
    
    def _is_locked_out(self, user_id: str) -> bool:
        """Check if user is locked out"""
        lockout_until = self._lockout_time.get(user_id)
        if lockout_until and datetime.now() < lockout_until:
            return True
        return False
    
    def _record_failed_attempt(self, user_id: str) -> None:
        """Record a failed login attempt"""
        attempts = self._failed_attempts.get(user_id, 0) + 1
        self._failed_attempts[user_id] = attempts
        
        # Lock account after 5 failed attempts
        if attempts >= 5:
            self._lockout_time[user_id] = datetime.now() + timedelta(minutes=15)
