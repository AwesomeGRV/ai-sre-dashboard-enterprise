import jwt
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class RBACManager:
    """Role-Based Access Control (RBAC) System"""
    
    def __init__(self):
        self.users = {
            "admin": {
                "password_hash": self._hash_password("admin123"),
                "roles": ["admin", "operator", "viewer"],
                "permissions": ["*"],
                "active": True,
                "last_login": None,
                "created_at": datetime.now().isoformat()
            },
            "operator": {
                "password_hash": self._hash_password("operator123"),
                "roles": ["operator", "viewer"],
                "permissions": [
                    "incidents:read", "incidents:create", "incidents:update",
                    "alerts:read", "alerts:acknowledge",
                    "metrics:read", "analytics:read"
                ],
                "active": True,
                "last_login": None,
                "created_at": datetime.now().isoformat()
            },
            "viewer": {
                "password_hash": self._hash_password("viewer123"),
                "roles": ["viewer"],
                "permissions": [
                    "incidents:read", "alerts:read", "metrics:read", "analytics:read"
                ],
                "active": True,
                "last_login": None,
                "created_at": datetime.now().isoformat()
            }
        }
        
        self.sessions = {}
        self.permission_matrix = {
            "incidents:read": ["admin", "operator", "viewer"],
            "incidents:create": ["admin", "operator"],
            "incidents:update": ["admin", "operator"],
            "incidents:delete": ["admin"],
            "alerts:read": ["admin", "operator", "viewer"],
            "alerts:acknowledge": ["admin", "operator"],
            "alerts:resolve": ["admin", "operator"],
            "metrics:read": ["admin", "operator", "viewer"],
            "analytics:read": ["admin", "operator", "viewer"],
            "system:read": ["admin"],
            "system:write": ["admin"],
            "audit:read": ["admin"],
            "users:read": ["admin"],
            "users:write": ["admin"]
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user info"""
        user = self.users.get(username)
        if not user:
            return None
        
        if not user.get("active", False):
            return None
        
        if user["password_hash"] != self._hash_password(password):
            return None
        
        # Update last login
        user["last_login"] = datetime.now().isoformat()
        
        # Create session
        session_token = self._generate_session_token(username)
        self.sessions[session_token] = {
            "username": username,
            "roles": user["roles"],
            "permissions": user["permissions"],
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        logger.info(f"User {username} authenticated successfully")
        return {
            "username": username,
            "roles": user["roles"],
            "permissions": user["permissions"],
            "session_token": session_token
        }
    
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Validate session token"""
        session = self.sessions.get(session_token)
        if not session:
            return None
        
        # Check if session expired
        if datetime.fromisoformat(session["expires_at"]) < datetime.now():
            # Remove expired session
            del self.sessions[session_token]
            return None
        
        return session
    
    def has_permission(self, session_token: str, required_permission: str) -> bool:
        """Check if user has required permission"""
        session = self.validate_session(session_token)
        if not session:
            return False
        
        user_permissions = session.get("permissions", [])
        
        # Check for wildcard permission
        if "*" in user_permissions:
            return True
        
        return required_permission in user_permissions
    
    def has_role(self, session_token: str, required_role: str) -> bool:
        """Check if user has required role"""
        session = self.validate_session(session_token)
        if not session:
            return False
        
        user_roles = session.get("roles", [])
        return required_role in user_roles
    
    def get_user_info(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from session"""
        session = self.validate_session(session_token)
        if not session:
            return None
        
        username = session.get("username")
        return {
            "username": username,
            "roles": session.get("roles", []),
            "permissions": session.get("permissions", []),
            "user_data": self.users.get(username, {})
        }
    
    def logout(self, session_token: str) -> bool:
        """Logout user by invalidating session"""
        if session_token in self.sessions:
            del self.sessions[session_token]
            logger.info(f"User logged out, session invalidated: {session_token}")
            return True
        return False
    
    def create_user(self, username: str, password: str, roles: List[str], 
                   permissions: List[str] = None, created_by: str = None) -> Dict[str, Any]:
        """Create new user (admin only)"""
        if permissions is None:
            # Default permissions based on highest role
            role_permissions = {
                "admin": ["*"],
                "operator": [
                    "incidents:read", "incidents:create", "incidents:update",
                    "alerts:read", "alerts:acknowledge",
                    "metrics:read", "analytics:read"
                ],
                "viewer": [
                    "incidents:read", "alerts:read", "metrics:read", "analytics:read"
                ]
            }
            permissions = []
            for role in roles:
                permissions.extend(role_permissions.get(role, []))
        
        self.users[username] = {
            "password_hash": self._hash_password(password),
            "roles": roles,
            "permissions": list(set(permissions)),
            "active": True,
            "last_login": None,
            "created_at": datetime.now().isoformat(),
            "created_by": created_by
        }
        
        logger.info(f"User {username} created with roles: {roles}")
        return {"message": f"User {username} created successfully"}
    
    def update_user_roles(self, username: str, new_roles: List[str], 
                      updated_by: str = None) -> Dict[str, Any]:
        """Update user roles (admin only)"""
        if username not in self.users:
            return {"error": "User not found"}
        
        user = self.users[username]
        
        # Calculate new permissions
        new_permissions = []
        for role in new_roles:
            for permission, allowed_roles in self.permission_matrix.items():
                if role in allowed_roles:
                    new_permissions.append(permission)
        
        user["roles"] = new_roles
        user["permissions"] = list(set(new_permissions))
        user["updated_by"] = updated_by
        user["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"User {username} roles updated to: {new_roles}")
        return {"message": f"User {username} updated successfully"}
    
    def deactivate_user(self, username: str, deactivated_by: str = None) -> Dict[str, Any]:
        """Deactivate user (admin only)"""
        if username not in self.users:
            return {"error": "User not found"}
        
        user = self.users[username]
        user["active"] = False
        user["deactivated_by"] = deactivated_by
        user["deactivated_at"] = datetime.now().isoformat()
        
        # Invalidate all sessions for this user
        sessions_to_remove = []
        for token, session in self.sessions.items():
            if session.get("username") == username:
                sessions_to_remove.append(token)
        
        for token in sessions_to_remove:
            del self.sessions[token]
        
        logger.info(f"User {username} deactivated")
        return {"message": f"User {username} deactivated successfully"}
    
    def get_permission_matrix(self) -> Dict[str, List[str]]:
        """Get permission matrix for reference"""
        return self.permission_matrix
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions (admin only)"""
        return [
            {**session, "session_token": token}
            for token, session in self.sessions.items()
            if datetime.fromisoformat(session["expires_at"]) > datetime.now()
        ]
    
    def _generate_session_token(self, username: str) -> str:
        """Generate secure session token"""
        payload = {
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "random": str(hash(username + str(datetime.now().timestamp())))
        }
        
        # In production, use proper JWT with secret key
        token = jwt.encode(payload, "your-secret-key", algorithm="HS256")
        return token.decode('utf-8')

# Global RBAC manager instance
rbac_manager = RBACManager()
