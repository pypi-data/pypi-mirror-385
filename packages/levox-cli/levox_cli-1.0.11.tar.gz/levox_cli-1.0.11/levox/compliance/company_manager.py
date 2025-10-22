import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from .evidence_store import EvidenceStore
from .models import CompanyProfile

class UserRole(Enum):
    """User roles within a company."""
    OWNER = "owner"
    ADMIN = "admin"
    VIEWER = "viewer"
    AUDITOR = "auditor"

@dataclass
class CompanyMember:
    """Represents a user's membership in a company."""
    user_id: str
    company_id: str
    role: UserRole
    joined_at: datetime
    invited_by: Optional[str] = None
    is_active: bool = True
    permissions: List[str] = None
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = self._get_default_permissions()
    
    def _get_default_permissions(self) -> List[str]:
        """Get default permissions based on role."""
        permissions_map = {
            UserRole.OWNER: [
                "read", "write", "delete", "admin", "invite_users", 
                "manage_settings", "export_data", "view_analytics"
            ],
            UserRole.ADMIN: [
                "read", "write", "delete", "invite_users", 
                "export_data", "view_analytics"
            ],
            UserRole.AUDITOR: [
                "read", "export_data", "view_analytics"
            ],
            UserRole.VIEWER: [
                "read", "view_analytics"
            ]
        }
        return permissions_map.get(self.role, [])

@dataclass
class CompanySettings:
    """Company-specific settings and preferences."""
    company_id: str
    scan_frequency_days: int = 7
    notification_enabled: bool = True
    auto_remediation_enabled: bool = False
    compliance_threshold: float = 80.0
    timezone: str = "UTC"
    language: str = "en"
    custom_fields: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_fields is None:
            self.custom_fields = {}

@dataclass
class CompanyInvitation:
    """Represents an invitation to join a company."""
    invitation_id: str
    company_id: str
    email: str
    role: UserRole
    invited_by: str
    invited_at: datetime
    expires_at: datetime
    status: str = "pending"  # pending, accepted, expired, revoked
    token: str = None
    
    def __post_init__(self):
        if self.token is None:
            self.token = str(uuid.uuid4())

class CompanyManager:
    """
    Manages multi-tenant company operations including user management,
    role-based access control, and company-specific settings.
    """
    
    def __init__(self, evidence_store: EvidenceStore):
        self.store = evidence_store
        self.logger = logging.getLogger(__name__)
        self._members_cache: Dict[str, List[CompanyMember]] = {}
        self._settings_cache: Dict[str, CompanySettings] = {}
    
    def create_company(self, owner_user_id: str, company_data: CompanyProfile) -> str:
        """
        Create a new company with the specified owner.
        
        Args:
            owner_user_id: ID of the user who will own the company
            company_data: Company profile information
            
        Returns:
            Company ID of the newly created company
        """
        try:
            # Generate company ID
            company_id = str(uuid.uuid4())
            
            # Update company profile with ID
            company_data.company_id = company_id
            company_data.created_at = datetime.now()
            company_data.updated_at = datetime.now()
            
            # Save company profile
            success = self.store.save_company_profile(company_data)
            if not success:
                raise Exception("Failed to save company profile")
            
            # Add owner as company member
            owner_member = CompanyMember(
                user_id=owner_user_id,
                company_id=company_id,
                role=UserRole.OWNER,
                joined_at=datetime.now()
            )
            
            self._add_company_member(owner_member)
            
            # Create default company settings
            default_settings = CompanySettings(
                company_id=company_id,
                scan_frequency_days=7,
                notification_enabled=True,
                auto_remediation_enabled=False,
                compliance_threshold=80.0,
                timezone="UTC",
                language="en"
            )
            
            self._save_company_settings(default_settings)
            
            self.logger.info(f"Created company {company_id} with owner {owner_user_id}")
            return company_id
            
        except Exception as e:
            self.logger.error(f"Failed to create company: {e}")
            raise
    
    def add_user_to_company(self, company_id: str, user_id: str, role: UserRole, 
                           invited_by: str) -> bool:
        """
        Add a user to a company with the specified role.
        
        Args:
            company_id: ID of the company
            user_id: ID of the user to add
            role: Role to assign to the user
            invited_by: ID of the user who invited them
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if user is already a member
            existing_member = self._get_company_member(company_id, user_id)
            if existing_member:
                self.logger.warning(f"User {user_id} is already a member of company {company_id}")
                return False
            
            # Create new member
            member = CompanyMember(
                user_id=user_id,
                company_id=company_id,
                role=role,
                joined_at=datetime.now(),
                invited_by=invited_by
            )
            
            success = self._add_company_member(member)
            if success:
                self.logger.info(f"Added user {user_id} to company {company_id} with role {role.value}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to add user to company: {e}")
            return False
    
    def invite_user_to_company(self, company_id: str, email: str, role: UserRole, 
                              invited_by: str) -> str:
        """
        Send an invitation to join a company.
        
        Args:
            company_id: ID of the company
            email: Email address to invite
            role: Role to assign upon acceptance
            invited_by: ID of the user sending the invitation
            
        Returns:
            Invitation ID
        """
        try:
            invitation_id = str(uuid.uuid4())
            invitation = CompanyInvitation(
                invitation_id=invitation_id,
                company_id=company_id,
                email=email,
                role=role,
                invited_by=invited_by,
                invited_at=datetime.now(),
                expires_at=datetime.now().replace(hour=23, minute=59, second=59) + 
                          timedelta(days=7)  # Expires in 7 days
            )
            
            # Save invitation (in a real implementation, this would be stored in database)
            self._save_invitation(invitation)
            
            # Send invitation email (placeholder)
            self._send_invitation_email(invitation)
            
            self.logger.info(f"Sent invitation {invitation_id} to {email} for company {company_id}")
            return invitation_id
            
        except Exception as e:
            self.logger.error(f"Failed to send invitation: {e}")
            raise
    
    def accept_invitation(self, invitation_token: str, user_id: str) -> bool:
        """
        Accept a company invitation.
        
        Args:
            invitation_token: Token from the invitation
            user_id: ID of the user accepting the invitation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            invitation = self._get_invitation_by_token(invitation_token)
            if not invitation:
                self.logger.error(f"Invalid invitation token: {invitation_token}")
                return False
            
            if invitation.status != "pending":
                self.logger.error(f"Invitation {invitation.invitation_id} is not pending")
                return False
            
            if datetime.now() > invitation.expires_at:
                self.logger.error(f"Invitation {invitation.invitation_id} has expired")
                invitation.status = "expired"
                self._save_invitation(invitation)
                return False
            
            # Add user to company
            success = self.add_user_to_company(
                invitation.company_id,
                user_id,
                invitation.role,
                invitation.invited_by
            )
            
            if success:
                invitation.status = "accepted"
                self._save_invitation(invitation)
                self.logger.info(f"User {user_id} accepted invitation {invitation.invitation_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to accept invitation: {e}")
            return False
    
    def remove_user_from_company(self, company_id: str, user_id: str, 
                                removed_by: str) -> bool:
        """
        Remove a user from a company.
        
        Args:
            company_id: ID of the company
            user_id: ID of the user to remove
            removed_by: ID of the user performing the removal
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if user is a member
            member = self._get_company_member(company_id, user_id)
            if not member:
                self.logger.warning(f"User {user_id} is not a member of company {company_id}")
                return False
            
            # Prevent removing the last owner
            if member.role == UserRole.OWNER:
                owners = [m for m in self.get_company_members(company_id) 
                         if m.role == UserRole.OWNER and m.is_active]
                if len(owners) <= 1:
                    self.logger.error("Cannot remove the last owner from company")
                    return False
            
            # Deactivate member
            member.is_active = False
            success = self._update_company_member(member)
            
            if success:
                self.logger.info(f"Removed user {user_id} from company {company_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to remove user from company: {e}")
            return False
    
    def update_user_role(self, company_id: str, user_id: str, new_role: UserRole, 
                        updated_by: str) -> bool:
        """
        Update a user's role in a company.
        
        Args:
            company_id: ID of the company
            user_id: ID of the user
            new_role: New role to assign
            updated_by: ID of the user making the change
            
        Returns:
            True if successful, False otherwise
        """
        try:
            member = self._get_company_member(company_id, user_id)
            if not member:
                self.logger.error(f"User {user_id} is not a member of company {company_id}")
                return False
            
            # Prevent demoting the last owner
            if member.role == UserRole.OWNER and new_role != UserRole.OWNER:
                owners = [m for m in self.get_company_members(company_id) 
                         if m.role == UserRole.OWNER and m.is_active]
                if len(owners) <= 1:
                    self.logger.error("Cannot demote the last owner")
                    return False
            
            member.role = new_role
            member.permissions = member._get_default_permissions()
            
            success = self._update_company_member(member)
            
            if success:
                self.logger.info(f"Updated user {user_id} role to {new_role.value} in company {company_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update user role: {e}")
            return False
    
    def get_company_members(self, company_id: str) -> List[CompanyMember]:
        """
        Get all active members of a company.
        
        Args:
            company_id: ID of the company
            
        Returns:
            List of company members
        """
        try:
            # Check cache first
            if company_id in self._members_cache:
                return self._members_cache[company_id]
            
            # Fetch from store (in a real implementation, this would query the database)
            members = self._fetch_company_members(company_id)
            
            # Filter active members
            active_members = [m for m in members if m.is_active]
            
            # Cache the result
            self._members_cache[company_id] = active_members
            
            return active_members
            
        except Exception as e:
            self.logger.error(f"Failed to get company members: {e}")
            return []
    
    def get_user_companies(self, user_id: str) -> List[str]:
        """
        Get all companies a user is a member of.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of company IDs
        """
        try:
            # In a real implementation, this would query the database
            companies = self._fetch_user_companies(user_id)
            return companies
            
        except Exception as e:
            self.logger.error(f"Failed to get user companies: {e}")
            return []
    
    def get_company_settings(self, company_id: str) -> Optional[CompanySettings]:
        """
        Get company settings.
        
        Args:
            company_id: ID of the company
            
        Returns:
            Company settings or None if not found
        """
        try:
            # Check cache first
            if company_id in self._settings_cache:
                return self._settings_cache[company_id]
            
            # Fetch from store
            settings = self._fetch_company_settings(company_id)
            
            if settings:
                self._settings_cache[company_id] = settings
            
            return settings
            
        except Exception as e:
            self.logger.error(f"Failed to get company settings: {e}")
            return None
    
    def update_company_settings(self, company_id: str, settings: CompanySettings, 
                               updated_by: str) -> bool:
        """
        Update company settings.
        
        Args:
            company_id: ID of the company
            settings: New settings
            updated_by: ID of the user making the change
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify user has permission to update settings
            member = self._get_company_member(company_id, updated_by)
            if not member or "manage_settings" not in member.permissions:
                self.logger.error(f"User {updated_by} does not have permission to update settings")
                return False
            
            settings.company_id = company_id
            success = self._save_company_settings(settings)
            
            if success:
                # Update cache
                self._settings_cache[company_id] = settings
                self.logger.info(f"Updated settings for company {company_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update company settings: {e}")
            return False
    
    def check_user_permission(self, company_id: str, user_id: str, permission: str) -> bool:
        """
        Check if a user has a specific permission in a company.
        
        Args:
            company_id: ID of the company
            user_id: ID of the user
            permission: Permission to check
            
        Returns:
            True if user has permission, False otherwise
        """
        try:
            member = self._get_company_member(company_id, user_id)
            if not member or not member.is_active:
                return False
            
            return permission in member.permissions
            
        except Exception as e:
            self.logger.error(f"Failed to check user permission: {e}")
            return False
    
    def get_user_role(self, company_id: str, user_id: str) -> Optional[UserRole]:
        """
        Get a user's role in a company.
        
        Args:
            company_id: ID of the company
            user_id: ID of the user
            
        Returns:
            User role or None if not found
        """
        try:
            member = self._get_company_member(company_id, user_id)
            if not member or not member.is_active:
                return None
            
            return member.role
            
        except Exception as e:
            self.logger.error(f"Failed to get user role: {e}")
            return None
    
    # Private helper methods (in a real implementation, these would interact with a database)
    
    def _add_company_member(self, member: CompanyMember) -> bool:
        """Add a company member to storage."""
        # Placeholder implementation
        return True
    
    def _get_company_member(self, company_id: str, user_id: str) -> Optional[CompanyMember]:
        """Get a specific company member."""
        # Placeholder implementation
        return None
    
    def _update_company_member(self, member: CompanyMember) -> bool:
        """Update a company member in storage."""
        # Placeholder implementation
        return True
    
    def _fetch_company_members(self, company_id: str) -> List[CompanyMember]:
        """Fetch all members of a company from storage."""
        # Placeholder implementation
        return []
    
    def _fetch_user_companies(self, user_id: str) -> List[str]:
        """Fetch all companies a user is a member of."""
        # Placeholder implementation
        return []
    
    def _save_company_settings(self, settings: CompanySettings) -> bool:
        """Save company settings to storage."""
        # Placeholder implementation
        return True
    
    def _fetch_company_settings(self, company_id: str) -> Optional[CompanySettings]:
        """Fetch company settings from storage."""
        # Placeholder implementation
        return None
    
    def _save_invitation(self, invitation: CompanyInvitation) -> bool:
        """Save invitation to storage."""
        # Placeholder implementation
        return True
    
    def _get_invitation_by_token(self, token: str) -> Optional[CompanyInvitation]:
        """Get invitation by token."""
        # Placeholder implementation
        return None
    
    def _send_invitation_email(self, invitation: CompanyInvitation) -> bool:
        """Send invitation email."""
        # Placeholder implementation
        self.logger.info(f"Would send invitation email to {invitation.email}")
        return True
