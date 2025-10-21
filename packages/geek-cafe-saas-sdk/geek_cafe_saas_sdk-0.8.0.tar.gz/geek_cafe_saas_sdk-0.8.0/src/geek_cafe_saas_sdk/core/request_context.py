"""
Request Context - Security Token Service for Geek Cafe SaaS SDK.

This module provides a centralized security context that tracks:
- Authenticated user (from JWT)
- Target resource (from API path parameters)
- Authorization helpers (roles, permissions, tenancy validation)
"""

from typing import Dict, List, Optional, Any


class RequestContext:
    """
    Security token service - single source of truth for request authentication and authorization.
    
    This class separates:
    - WHO is making the request (authenticated_user_id, authenticated_tenant_id from JWT)
    - WHAT they're trying to access (target_user_id, target_tenant_id from path)
    
    This separation enables proper security validation:
    - Can user A access resources belonging to user B?
    - Can user from tenant X access resources in tenant Y?
    - Does user have required role/permission?
    """
    
    def __init__(self, user_context: Optional[Dict[str, Any]] = None):
        """
        Initialize request context from JWT payload.
        
        Args:
            user_context: Dictionary from JWT containing:
                - user_id: Authenticated user ID
                - tenant_id: Authenticated user's tenant ID
                - roles: List of role strings
                - permissions: List of permission strings
                - email: User email
                - inboxes: List of inbox IDs (optional)
        """
        self._user_context = user_context or {}
        
        # Authenticated user (from JWT)
        self.authenticated_user_id: Optional[str] = self._user_context.get('user_id')
        self.authenticated_tenant_id: Optional[str] = self._user_context.get('tenant_id')
        self.authenticated_user_email: Optional[str] = self._user_context.get('email')
        self.roles: List[str] = self._user_context.get('roles', [])
        self.permissions: List[str] = self._user_context.get('permissions', [])
        self.inboxes: List[str] = self._user_context.get('inboxes', [])
        
        # Target resource (from path parameters - set by services)
        self.target_user_id: Optional[str] = None
        self.target_tenant_id: Optional[str] = None
    
    def set_targets(self, tenant_id: Optional[str] = None, user_id: Optional[str] = None):
        """
        Set target resource IDs from path parameters.
        
        Args:
            tenant_id: Target tenant ID from path
            user_id: Target user ID from path
        """
        if tenant_id:
            self.target_tenant_id = tenant_id
        if user_id:
            self.target_user_id = user_id
    
    # ========================================
    # Tenancy Validation
    # ========================================
    
    def is_same_tenancy(self) -> bool:
        """Check if authenticated user's tenant matches target tenant."""
        if not self.target_tenant_id:
            return True  # No target specified, assume same
        return self.authenticated_tenant_id == self.target_tenant_id
    
    def validate_tenant_access(self, tenant_id: str) -> bool:
        """
        Validate user can access resources in target tenant.
        
        Args:
            tenant_id: Tenant ID to validate
            
        Returns:
            True if access allowed, False otherwise
        """
        # Platform admins can access any tenant
        if self.is_platform_admin():
            return True
        
        # Regular users can only access their own tenant
        return self.authenticated_tenant_id == tenant_id
    
    # ========================================
    # User Access Validation
    # ========================================
    
    def is_self_user(self) -> bool:
        """Check if authenticated user is the same as target user."""
        if not self.target_user_id:
            return True  # No target specified
        return self.authenticated_user_id == self.target_user_id
    
    def can_access_user_resource(self, resource_user_id: str) -> bool:
        """
        Check if user can access a resource owned by another user.
        
        Args:
            resource_user_id: Owner of the resource
            
        Returns:
            True if access allowed
        """
        # Self access
        if self.authenticated_user_id == resource_user_id:
            return True
        
        # Admins can access
        if self.is_platform_admin() or self.is_tenant_admin():
            return True
        
        return False
    
    # ========================================
    # Role Checks
    # ========================================
    
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.roles
    
    def has_any_role(self, roles: List[str]) -> bool:
        """Check if user has any of the specified roles."""
        return any(role in self.roles for role in roles)
    
    def is_platform_admin(self) -> bool:
        """Check if user is a platform admin (can access all tenants)."""
        return 'platform_admin' in self.roles
    
    def is_tenant_admin(self) -> bool:
        """Check if user is admin of their tenant."""
        return 'tenant_admin' in self.roles
    
    def is_admin(self) -> bool:
        """Check if user is any kind of admin."""
        return self.is_platform_admin() or self.is_tenant_admin()
    
    # ========================================
    # Permission Checks
    # ========================================
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions
    
    def has_any_permission(self, permissions: List[str]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(perm in self.permissions for perm in permissions)
    
    def has_all_permissions(self, permissions: List[str]) -> bool:
        """Check if user has all specified permissions."""
        return all(perm in self.permissions for perm in permissions)
    
    # ========================================
    # Utility Methods
    # ========================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for logging/debugging."""
        return {
            'authenticated_user_id': self.authenticated_user_id,
            'authenticated_tenant_id': self.authenticated_tenant_id,
            'authenticated_user_email': self.authenticated_user_email,
            'target_user_id': self.target_user_id,
            'target_tenant_id': self.target_tenant_id,
            'roles': self.roles,
            'permissions': self.permissions,
            'is_admin': self.is_admin(),
            'is_same_tenancy': self.is_same_tenancy(),
            'is_self_user': self.is_self_user(),
        }
    
    def __repr__(self) -> str:
        return f"RequestContext(user={self.authenticated_user_id}, tenant={self.authenticated_tenant_id})"
