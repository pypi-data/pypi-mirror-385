"""
Geek Cafe, LLC
MIT License.  See Project Root for the license information.

ChatChannelService for managing chat channels (Slack-like functionality).
"""

from typing import Dict, Any, Optional, List
from boto3_assist.dynamodb.dynamodb import DynamoDB
from boto3_assist.dynamodb.dynamodb_index import DynamoDBKey
from geek_cafe_saas_sdk.services.database_service import DatabaseService
from geek_cafe_saas_sdk.core.service_result import ServiceResult
from geek_cafe_saas_sdk.core.service_errors import ValidationError, NotFoundError, AccessDeniedError
from geek_cafe_saas_sdk.domains.messaging.models import ChatChannel, ChatChannelMember
import datetime as dt


class ChatChannelService(DatabaseService[ChatChannel]):
    """Service for ChatChannel database operations."""

    def __init__(self, *, dynamodb: DynamoDB = None, table_name: str = None):
        super().__init__(dynamodb=dynamodb, table_name=table_name)

    def create(self, tenant_id: str, user_id: str, payload: Dict[str, Any]) -> ServiceResult[ChatChannel]:
        """
        Create a new chat channel from a payload.
        
        Args:
            tenant_id: Tenant ID
            user_id: Owner user ID (who the channel belongs to)
            payload: Channel data including:
                - name: Channel name (required)
                - created_by_id: Admin who created it (optional, for audit trail)
            
        Returns:
            ServiceResult with ChatChannel
        """
        try:
            # Validate required fields
            required_fields = ['name']
            self._validate_required_fields(payload, required_fields)

            # Create and map channel instance from the payload
            channel = ChatChannel().map(payload)
            channel.tenant_id = tenant_id
            channel.user_id = user_id  # Owner
            
            # Set created_by from payload if provided (admin scenario), else use owner
            if not channel.created_by_id:
                channel.created_by_id = user_id
            if not channel.created_by:
                channel.created_by = user_id

            # Set defaults
            if not channel.channel_type:
                channel.channel_type = "public"

            # Prepare for save (sets ID and timestamps)
            channel.prep_for_save()

            # Save channel metadata
            save_result = self._save_model(channel)
            if not save_result.success:
                return save_result

            # Add creator as the first member
            member_result = self._add_member_record(channel.id, user_id, user_id, role="owner")
            if not member_result.success:
                # Rollback channel creation if member add fails
                # In production, consider using transactions
                return member_result
            
            channel.increment_member_count()
            self._save_model(channel)

            return ServiceResult.success_result(channel)

        except Exception as e:
            return self._handle_service_exception(e, 'create_chat_channel', tenant_id=tenant_id, user_id=user_id)

    def get_by_id(self, resource_id: str, tenant_id: str, user_id: str) -> ServiceResult[ChatChannel]:
        """
        Get chat channel by ID with access control.
        
        Args:
            resource_id: Channel ID
            tenant_id: Tenant ID
            user_id: User ID requesting access
            
        Returns:
            ServiceResult with ChatChannel
        """
        try:
            channel = self._get_model_by_id(resource_id, ChatChannel)

            if not channel:
                raise NotFoundError(f"Chat channel with ID {resource_id} not found")

            # Check if deleted
            if channel.is_deleted():
                raise NotFoundError(f"Chat channel with ID {resource_id} not found")

            # Validate tenant access
            if hasattr(channel, 'tenant_id'):
                self._validate_tenant_access(channel.tenant_id, tenant_id)

            # Check if user can access this channel
            # Public channels: everyone can access
            # Private channels: only members can access
            if channel.channel_type == "private":
                if not self.is_member(resource_id, user_id):
                    raise AccessDeniedError("Access denied to this private channel")

            return ServiceResult.success_result(channel)

        except Exception as e:
            return self._handle_service_exception(e, 'get_chat_channel', resource_id=resource_id, tenant_id=tenant_id)

    def list_by_type(self, tenant_id: str, channel_type: str, user_id: str,
                     limit: int = 50) -> ServiceResult[List[ChatChannel]]:
        """
        List chat channels by type using GSI1.
        
        Args:
            tenant_id: Tenant ID
            channel_type: Channel type filter (public, private, direct)
            user_id: User ID for access control
            limit: Maximum number of results
            
        Returns:
            ServiceResult with list of ChatChannels
        """
        try:
            temp_channel = ChatChannel()
            temp_channel.tenant_id = tenant_id
            temp_channel.channel_type = channel_type

            result = self._query_by_index(
                temp_channel,
                "gsi1",
                ascending=False,  # Most recent activity first
                limit=limit
            )

            if not result.success:
                return result

            # Filter: public channels visible to all, private only if member
            accessible_channels = []
            for channel in result.data:
                if not channel.is_deleted():
                    if channel.channel_type == "public" or self.is_member(channel.id, user_id):
                        accessible_channels.append(channel)

            return ServiceResult.success_result(accessible_channels)

        except Exception as e:
            return self._handle_service_exception(e, 'list_channels_by_type',
                                                tenant_id=tenant_id, channel_type=channel_type)

    def list_all(self, tenant_id: str, user_id: str, limit: int = 100) -> ServiceResult[List[ChatChannel]]:
        """
        List all chat channels for a tenant using GSI2.
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID for access control
            limit: Maximum number of results
            
        Returns:
            ServiceResult with list of ChatChannels
        """
        try:
            temp_channel = ChatChannel()
            temp_channel.tenant_id = tenant_id

            result = self._query_by_index(
                temp_channel,
                "gsi2",
                ascending=True,  # Alphabetical by name
                limit=limit
            )

            if not result.success:
                return result

            # Filter accessible channels
            accessible_channels = []
            for channel in result.data:
                if not channel.is_deleted():
                    if channel.channel_type == "public" or self.is_member(channel.id, user_id):
                        accessible_channels.append(channel)

            return ServiceResult.success_result(accessible_channels)

        except Exception as e:
            return self._handle_service_exception(e, 'list_all_channels', tenant_id=tenant_id)

    def list_default_channels(self, tenant_id: str, limit: int = 50) -> ServiceResult[List[ChatChannel]]:
        """
        List default channels (auto-join for new users) using GSI3.
        
        Args:
            tenant_id: Tenant ID
            limit: Maximum number of results
            
        Returns:
            ServiceResult with list of default ChatChannels
        """
        try:
            temp_channel = ChatChannel()
            temp_channel.tenant_id = tenant_id
            temp_channel.is_default = True

            result = self._query_by_index(
                temp_channel,
                "gsi3",
                ascending=False,
                limit=limit
            )

            if not result.success:
                return result

            # Filter out deleted channels
            active_channels = [c for c in result.data if not c.is_deleted()]
            return ServiceResult.success_result(active_channels)

        except Exception as e:
            return self._handle_service_exception(e, 'list_default_channels', tenant_id=tenant_id)

    def list_user_channels(self, tenant_id: str, user_id: str, 
                           include_archived: bool = False, limit: int = 100) -> ServiceResult[List[ChatChannel]]:
        """
        List all channels a user is a member of.
        
        Uses GSI1 for fast lookup via membership records.
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID
            include_archived: Whether to include archived channels
            limit: Maximum number of results
            
        Returns:
            ServiceResult with list of ChatChannels
        """
        try:
            # Get user's channel memberships (fast via GSI1)
            memberships_result = self.list_user_channels_fast(user_id, limit)
            if not memberships_result.success:
                return memberships_result

            # Fetch full channel details for each membership
            user_channels = []
            for membership in memberships_result.data:
                channel = self._get_model_by_id(membership["channel_id"], ChatChannel)
                if channel and not channel.is_deleted():
                    # Filter by tenant and archived status
                    if channel.tenant_id == tenant_id:
                        if include_archived or not channel.is_archived:
                            user_channels.append(channel)

            # Sort by last activity
            user_channels.sort(key=lambda c: c.last_message_at or c.created_utc_ts, reverse=True)

            return ServiceResult.success_result(user_channels)

        except Exception as e:
            return self._handle_service_exception(e, 'list_user_channels',
                                                tenant_id=tenant_id, user_id=user_id)

    def add_member(self, channel_id: str, tenant_id: str, user_id: str,
                   member_to_add: str) -> ServiceResult[ChatChannel]:
        """
        Add a member to a chat channel.
        
        Args:
            channel_id: Channel ID
            tenant_id: Tenant ID
            user_id: User ID performing the action
            member_to_add: User ID to add as member
            
        Returns:
            ServiceResult with updated ChatChannel
        """
        try:
            channel_result = self.get_by_id(channel_id, tenant_id, user_id)
            if not channel_result.success:
                return channel_result

            channel = channel_result.data

            # For private channels, only members can add new members
            if channel.channel_type == "private" and not self.is_member(channel_id, user_id):
                raise AccessDeniedError("Only members can add new members to private channels")

            # Check if already a member
            if self.is_member(channel_id, member_to_add):
                return ServiceResult.success_result(channel)  # Already a member, no-op

            # Add member record
            member_result = self._add_member_record(channel_id, member_to_add, user_id)
            if not member_result.success:
                return member_result

            # Update member count
            channel.increment_member_count()
            channel.updated_by_id = user_id
            channel.prep_for_save()
            self._save_model(channel)

            return ServiceResult.success_result(channel)

        except Exception as e:
            return self._handle_service_exception(e, 'add_channel_member',
                                                channel_id=channel_id, member_to_add=member_to_add)

    def remove_member(self, channel_id: str, tenant_id: str, user_id: str,
                      member_to_remove: str) -> ServiceResult[ChatChannel]:
        """
        Remove a member from a chat channel.
        
        Args:
            channel_id: Channel ID
            tenant_id: Tenant ID
            user_id: User ID performing the action
            member_to_remove: User ID to remove
            
        Returns:
            ServiceResult with updated ChatChannel
        """
        try:
            channel_result = self.get_by_id(channel_id, tenant_id, user_id)
            if not channel_result.success:
                return channel_result

            channel = channel_result.data

            # Users can remove themselves, or creator can remove others
            if user_id != member_to_remove and channel.created_by != user_id:
                raise AccessDeniedError("Only channel creator can remove other members")

            # Check if member exists
            if not self.is_member(channel_id, member_to_remove):
                return ServiceResult.success_result(channel)  # Not a member, no-op

            # Delete member record using adjacent record pattern
            pk = DynamoDBKey.build_key(("channel", channel_id))
            sk = DynamoDBKey.build_key(("member", member_to_remove))
            
            delete_result = self._delete_by_composite_key(pk=pk, sk=sk)
            if not delete_result.success:
                return delete_result

            # Update member count
            channel.decrement_member_count()
            channel.updated_by_id = user_id
            channel.prep_for_save()
            self._save_model(channel)

            return ServiceResult.success_result(channel)

        except Exception as e:
            return self._handle_service_exception(e, 'remove_channel_member',
                                                channel_id=channel_id, member_to_remove=member_to_remove)

    def update_last_message(self, channel_id: str, tenant_id: str, 
                            message_id: str, timestamp: float) -> ServiceResult[ChatChannel]:
        """
        Update channel's last message tracking (called by ChatMessageService).
        
        Args:
            channel_id: Channel ID
            tenant_id: Tenant ID
            message_id: ID of the last message
            timestamp: Timestamp of the message
            
        Returns:
            ServiceResult with updated ChatChannel
        """
        try:
            channel = self._get_model_by_id(channel_id, ChatChannel)
            if not channel:
                raise NotFoundError(f"Chat channel with ID {channel_id} not found")

            # Validate tenant
            self._validate_tenant_access(channel.tenant_id, tenant_id)

            channel.update_last_message(message_id, timestamp)
            channel.prep_for_save()

            return self._save_model(channel)

        except Exception as e:
            return self._handle_service_exception(e, 'update_channel_last_message',
                                                channel_id=channel_id)

    def archive(self, channel_id: str, tenant_id: str, user_id: str) -> ServiceResult[ChatChannel]:
        """
        Archive a chat channel.
        
        Args:
            channel_id: Channel ID
            tenant_id: Tenant ID
            user_id: User ID performing the action
            
        Returns:
            ServiceResult with updated ChatChannel
        """
        try:
            channel_result = self.get_by_id(channel_id, tenant_id, user_id)
            if not channel_result.success:
                return channel_result

            channel = channel_result.data

            # Only creator can archive
            if channel.created_by != user_id:
                raise AccessDeniedError("Only channel creator can archive the channel")

            channel.is_archived = True
            channel.updated_by_id = user_id
            channel.prep_for_save()

            return self._save_model(channel)

        except Exception as e:
            return self._handle_service_exception(e, 'archive_channel', channel_id=channel_id)

    def unarchive(self, channel_id: str, tenant_id: str, user_id: str) -> ServiceResult[ChatChannel]:
        """
        Unarchive a chat channel.
        
        Args:
            channel_id: Channel ID
            tenant_id: Tenant ID
            user_id: User ID performing the action
            
        Returns:
            ServiceResult with updated ChatChannel
        """
        try:
            # For unarchive, we need to get the channel even if archived
            channel = self._get_model_by_id(channel_id, ChatChannel)
            if not channel:
                raise NotFoundError(f"Chat channel with ID {channel_id} not found")

            self._validate_tenant_access(channel.tenant_id, tenant_id)

            # Only creator can unarchive
            if channel.created_by != user_id:
                raise AccessDeniedError("Only channel creator can unarchive the channel")

            channel.is_archived = False
            channel.updated_by_id = user_id
            channel.prep_for_save()

            return self._save_model(channel)

        except Exception as e:
            return self._handle_service_exception(e, 'unarchive_channel', channel_id=channel_id)

    def update(self, resource_id: str, tenant_id: str, user_id: str,
               updates: Dict[str, Any]) -> ServiceResult[ChatChannel]:
        """
        Update chat channel with access control.
        
        Args:
            resource_id: Channel ID
            tenant_id: Tenant ID
            user_id: User ID performing the update
            updates: Dictionary of fields to update
            
        Returns:
            ServiceResult with updated ChatChannel
        """
        try:
            channel = self._get_model_by_id(resource_id, ChatChannel)

            if not channel:
                raise NotFoundError(f"Chat channel with ID {resource_id} not found")

            # Validate tenant access
            if hasattr(channel, 'tenant_id'):
                self._validate_tenant_access(channel.tenant_id, tenant_id)

            # Check permissions - only creator or members can update
            if not self.is_member(resource_id, user_id):
                raise AccessDeniedError("Only channel members can update the channel")

            # Apply updates (limited fields)
            allowed_fields = ['name', 'description', 'topic', 'icon', 'is_announcement', 'is_default']
            for field, value in updates.items():
                if field in allowed_fields and hasattr(channel, field):
                    # Only creator can change certain settings
                    if field in ['is_announcement', 'is_default'] and channel.created_by != user_id:
                        continue
                    setattr(channel, field, value)

            # Update metadata
            channel.updated_by_id = user_id
            channel.prep_for_save()

            # Save updated channel
            return self._save_model(channel)

        except Exception as e:
            return self._handle_service_exception(e, 'update_chat_channel', resource_id=resource_id, tenant_id=tenant_id)

    def delete(self, resource_id: str, tenant_id: str, user_id: str) -> ServiceResult[bool]:
        """
        Soft delete chat channel with access control.
        
        Args:
            resource_id: Channel ID
            tenant_id: Tenant ID
            user_id: User ID performing the deletion
            
        Returns:
            ServiceResult with boolean success
        """
        try:
            channel = self._get_model_by_id(resource_id, ChatChannel)

            if not channel:
                raise NotFoundError(f"Chat channel with ID {resource_id} not found")

            # Check if already deleted
            if channel.is_deleted():
                return ServiceResult.success_result(True)

            # Validate tenant access
            if hasattr(channel, 'tenant_id'):
                self._validate_tenant_access(channel.tenant_id, tenant_id)

            # Only creator can delete
            if channel.created_by != user_id:
                raise AccessDeniedError("Only channel creator can delete the channel")

            # Soft delete: set deleted timestamp and metadata
            channel.deleted_utc_ts = dt.datetime.now(dt.UTC).timestamp()
            channel.deleted_by_id = user_id
            channel.prep_for_save()

            # Save the updated channel
            save_result = self._save_model(channel)
            if save_result.success:
                return ServiceResult.success_result(True)
            else:
                return save_result

        except Exception as e:
            return self._handle_service_exception(e, 'delete_chat_channel', resource_id=resource_id, tenant_id=tenant_id)

    # Membership Management Methods (using adjacent records for scalability)

    def _add_member_record(self, channel_id: str, user_id: str, added_by_id: str, 
                          role: str = "member") -> ServiceResult[ChatChannelMember]:
        """
        Add a member record to the channel (internal helper).
        
        Args:
            channel_id: Channel ID
            user_id: User ID to add as member
            added_by_id: User ID performing the add
            role: Member role (owner, admin, member)
            
        Returns:
            ServiceResult with ChatChannelMember
        """
        try:
            member = ChatChannelMember()
            member.channel_id = channel_id
            member.user_id = user_id
            member.role = role
            member.joined_at = dt.datetime.now(dt.UTC).timestamp()
            member.added_by_id = added_by_id
            member.tenant_id = None  # Inherited from channel
            member.prep_for_save()
            
            return self._save_model(member)
        except Exception as e:
            return self._handle_service_exception(e, 'add_member_record', 
                                                 channel_id=channel_id, user_id=user_id)

    def is_member(self, channel_id: str, user_id: str) -> bool:
        """
        Check if a user is a member of a channel (fast lookup).
        Uses adjacent record pattern: pk="channel#<id>", sk="member#<user_id>"
        
        Args:
            channel_id: Channel ID
            user_id: User ID to check
            
        Returns:
            True if user is a member, False otherwise
        """
        try:
            # Build composite key for adjacent record lookup
            pk = DynamoDBKey.build_key(("channel", channel_id))
            sk = DynamoDBKey.build_key(("member", user_id))
            key = {"pk": pk, "sk": sk}
            
            result = self.dynamodb.get(table_name=self.table_name, key=key)
            return result and "Item" in result
        except Exception:
            return False

    def get_member(self, channel_id: str, user_id: str) -> Optional[ChatChannelMember]:
        """
        Get member record for a user in a channel.
        Uses adjacent record pattern: pk="channel#<id>", sk="member#<user_id>"
        
        Args:
            channel_id: Channel ID
            user_id: User ID
            
        Returns:
            ChatChannelMember if found, None otherwise
        """
        try:
            # Build composite key for adjacent record lookup
            pk = DynamoDBKey.build_key(("channel", channel_id))
            sk = DynamoDBKey.build_key(("member", user_id))
            key = {"pk": pk, "sk": sk}
            
            result = self.dynamodb.get(table_name=self.table_name, key=key)
            if result and "Item" in result:
                member_obj = ChatChannelMember()
                member_obj.map(result["Item"])
                return member_obj
            return None
        except Exception:
            return None

    def list_channel_members(self, channel_id: str, limit: int = 100) -> ServiceResult[List[ChatChannelMember]]:
        """
        List all members of a channel (paginated).
        
        Args:
            channel_id: Channel ID
            limit: Maximum number of members to return
            
        Returns:
            ServiceResult with list of ChatChannelMembers
        """
        try:
            # Query for all members in this channel using adjacent record pattern
            pk = DynamoDBKey.build_key(("channel", channel_id))
            
            return self._query_by_pk_with_sk_prefix(
                model_class=ChatChannelMember,
                pk=pk,
                sk_prefix="member#",
                limit=limit
            )
        except Exception as e:
            return self._handle_service_exception(e, 'list_channel_members', channel_id=channel_id)

    def list_user_channels_fast(self, user_id: str, limit: int = 100) -> ServiceResult[List[Dict[str, Any]]]:
        """
        List all channels a user is a member of (using GSI1 for fast lookup).
        
        Args:
            user_id: User ID
            limit: Maximum number of channels to return
            
        Returns:
            ServiceResult with list of channel membership records
        """
        try:
            # Query GSI1 for all channels this user is in
            temp_member = ChatChannelMember()
            temp_member.user_id = user_id
            
            result = self._query_by_index(
                model=temp_member,
                index_name="gsi1",
                limit=limit
            )
            
            if not result.success:
                return result
            
            # Extract channel info from memberships
            memberships = []
            for member in result.data:
                memberships.append({
                    "channel_id": member.channel_id,
                    "role": member.role,
                    "joined_at": member.joined_at,
                    "last_read_at": member.last_read_at
                })
            
            return ServiceResult.success_result(memberships)
        except Exception as e:
            return self._handle_service_exception(e, 'list_user_channels_fast', user_id=user_id)
    
    # Removed custom _handle_service_exception - using base class implementation from DatabaseService
