# Event Service (Refactored for location-based discovery and timestamps)

from typing import Dict, Any, Optional, List, Tuple
from boto3_assist.dynamodb.dynamodb import DynamoDB
from geek_cafe_saas_sdk.services.database_service import DatabaseService
from geek_cafe_saas_sdk.core.service_result import ServiceResult
from geek_cafe_saas_sdk.core.service_errors import ValidationError, NotFoundError, AccessDeniedError
from geek_cafe_saas_sdk.domains.events.models import Event, EventAttendee
from geek_cafe_saas_sdk.utilities.dynamodb_utils import build_projection_with_reserved_keywords
import datetime as dt
import math


class EventService(DatabaseService[Event]):
    """
    Service for Event database operations (refactored for location-based discovery).
    
    Features:
    - Timestamp-based date fields (float UTC timestamps)
    - Location-based queries (city, state, geo)
    - Automatic EventAttendee creation for owner
    - Capacity management
    - Multi-host support via EventAttendee
    """
    

    def create(self, tenant_id: str, user_id: str, create_organizer_attendee: bool = True,
               **kwargs) -> ServiceResult[Event]:
        """
        Create a new event.
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID (becomes owner_id)
            create_organizer_attendee: Auto-create EventAttendee for organizer
            **kwargs: Event fields
            
        Required kwargs: title, start_utc_ts (or start_datetime)
        """
        try:
            # Validate required fields
            if not kwargs.get('title'):
                raise ValidationError("Title is required")

            # Handle datetime conversion (support multiple field names)
            start_utc_ts = kwargs.get('start_utc_ts')
            if not start_utc_ts and kwargs.get('start_datetime'):
                start_utc_ts = Event.datetime_to_utc_ts(kwargs['start_datetime'])
                kwargs['start_utc_ts'] = start_utc_ts
            elif not start_utc_ts and kwargs.get('date'):
                # Support legacy 'date' field
                start_utc_ts = Event.datetime_to_utc_ts(kwargs['date'])
                kwargs['start_utc_ts'] = start_utc_ts
            
            if not start_utc_ts:
                raise ValidationError("start_utc_ts or start_datetime or date is required")

            # Validate date is in future (only skip for explicitly draft status)
            status = kwargs.get('status')
            # Only allow past dates if status is explicitly set to 'draft'
            if status != 'draft' and start_utc_ts < dt.datetime.now(dt.UTC).timestamp():
                raise ValidationError("Event start time must be in the future")

            # Create event instance
            event = Event().map(kwargs)
            event.owner_id = user_id  # Primary owner
            event.tenant_id = tenant_id
            event.user_id = user_id
            event.created_by_id = user_id

            # Set defaults
            if not event.status:
                event.status = 'draft'
            if not event.visibility:
                event.visibility = 'public'

            # Prepare for save
            event.prep_for_save()

            # Save to database
            save_result = self._save_model(event)
            
            if save_result.success and create_organizer_attendee:
                # Create EventAttendee record for organizer
                from .event_attendee_service import EventAttendeeService
                attendee_service = EventAttendeeService(
                    dynamodb=self.dynamodb,
                    table_name=self.table_name,
                    request_context=self._request_context
                )
                
                attendee_result = attendee_service.invite(
                    event_id=event.id,
                    user_id=user_id,
                    tenant_id=tenant_id,
                    invited_by_user_id=user_id,
                    role='organizer',
                    rsvp_status='accepted'
                )
                
                # Don't fail event creation if attendee creation fails
                if not attendee_result.success:
                    print(f"Warning: Failed to create attendee record for organizer: {attendee_result.error}")

            return save_result

        except Exception as e:
            return self._handle_service_exception(e, 'create_event', tenant_id=tenant_id, user_id=user_id)

    def get_by_id(self, resource_id: str, tenant_id: str, user_id: str) -> ServiceResult[Event]:
        """Get event by ID with access control."""
        try:
            event = self._get_model_by_id(resource_id, Event)

            if not event:
                raise NotFoundError(f"Event with ID {resource_id} not found")

            # Check if deleted
            if event.is_deleted():
                raise NotFoundError(f"Event with ID {resource_id} not found")

            # Validate tenant access
            if hasattr(event, 'tenant_id'):
                self._validate_tenant_access(event.tenant_id, tenant_id)

            return ServiceResult.success_result(event)

        except Exception as e:
            return self._handle_service_exception(e, 'get_event', resource_id=resource_id, tenant_id=tenant_id)

    def list_by_owner(self, owner_id: str, tenant_id: str, limit: int = 50) -> ServiceResult[List[Event]]:
        """
        Get events by owner (primary organizer) using GSI1.
        
        Args:
            owner_id: Owner user ID
            tenant_id: Tenant ID
            limit: Max results
        """
        try:
            temp_event = Event()
            temp_event.owner_id = owner_id

            result = self._query_by_index(
                temp_event,
                "gsi1",
                ascending=False,  # Most recent first
                limit=limit
            )

            if not result.success:
                return result

            # Filter out deleted events and validate tenant
            active_events = []
            for event in result.data:
                if not event.is_deleted() and event.tenant_id == tenant_id:
                    active_events.append(event)

            return ServiceResult.success_result(active_events)

        except Exception as e:
            return self._handle_service_exception(e, 'list_by_owner', owner_id=owner_id)

    def list_by_city(self, city: str, state: str, country: str, tenant_id: str,
                     start_date: float = None, end_date: float = None,
                     limit: int = 50) -> ServiceResult[List[Event]]:
        """
        Get events by city using GSI2 (city#state#country).
        
        Args:
            city: City name
            state: State/Province/Region
            country: Country code
            tenant_id: Tenant ID
            start_date: Optional start date filter (UTC timestamp)
            end_date: Optional end date filter (UTC timestamp)
            limit: Max results
        """
        try:
            temp_event = Event()
            temp_event.location_city = city
            temp_event.location_state = state
            temp_event.location_country = country

            # Use helper method for query
            result = self._query_by_index(
                model=temp_event,
                index_name="gsi2",
                ascending=True,  # Upcoming events first
                limit=limit
            )

            if not result.success:
                return result

            # Post-query filtering
            valid_events = []
            for event in result.data:
                # Tenant isolation and deleted check
                if event.tenant_id != tenant_id or event.is_deleted():
                    continue
                
                # Date range filter if specified
                if start_date and end_date:
                    if not (start_date <= event.start_utc_ts <= end_date):
                        continue
                
                valid_events.append(event)

            return ServiceResult.success_result(valid_events)

        except Exception as e:
            return self._handle_service_exception(e, 'list_by_city', city=city, state=state, country=country)

    def list_by_state(self, state: str, country: str, tenant_id: str,
                     limit: int = 50) -> ServiceResult[List[Event]]:
        """
        Get events by state/region using GSI3.
        
        Args:
            state: State/Province/Region
            country: Country code
            tenant_id: Tenant ID
            limit: Max results
        """
        try:
            temp_event = Event()
            temp_event.location_state = state
            temp_event.location_country = country

            # Use helper method for query
            result = self._query_by_index(
                model=temp_event,
                index_name="gsi3",
                ascending=True,
                limit=limit
            )

            if not result.success:
                return result

            # Post-query filtering
            valid_events = [
                event for event in result.data
                if event.tenant_id == tenant_id and not event.is_deleted()
            ]

            return ServiceResult.success_result(valid_events)

        except Exception as e:
            return self._handle_service_exception(e, 'list_by_state', state=state, country=country)

    def list_nearby(self, latitude: float, longitude: float, radius_km: float,
                   tenant_id: str, limit: int = 50) -> ServiceResult[List[Event]]:
        """
        Get events near a location using GSI4 (geo-location).
        
        Uses geohash for approximate location then filters by actual distance.
        
        Args:
            latitude: Latitude
            longitude: Longitude
            radius_km: Search radius in kilometers
            tenant_id: Tenant ID
            limit: Max results
        """
        try:
            # Create temp event to get geohash
            temp_event = Event()
            temp_event.location_latitude = latitude
            temp_event.location_longitude = longitude
            
            geohash = temp_event._get_geohash()
            if not geohash:
                return ServiceResult.error_result("Invalid coordinates", "INVALID_COORDINATES")

            # Use helper method for query (get more results for distance filtering)
            result = self._query_by_index(
                model=temp_event,
                index_name="gsi4",
                ascending=True,
                limit=limit * 3  # Get extra to filter by distance
            )

            if not result.success:
                return result

            # Filter by actual distance and tenant
            nearby_events = []
            for event in result.data:
                # Tenant isolation and deleted check
                if event.tenant_id != tenant_id or event.is_deleted():
                    continue
                
                if event.has_location_coordinates():
                    distance = self._calculate_distance(
                        latitude, longitude,
                        event.location_latitude, event.location_longitude
                    )
                    if distance <= radius_km:
                        nearby_events.append(event)
                        if len(nearby_events) >= limit:
                            break

            return ServiceResult.success_result(nearby_events)

        except Exception as e:
            return self._handle_service_exception(e, 'list_nearby', latitude=latitude, longitude=longitude)

    def list_by_type(self, event_type: str, tenant_id: str, status: str = 'published',
                    limit: int = 50) -> ServiceResult[List[Event]]:
        """
        Get events by type using GSI6.
        
        Args:
            event_type: Event type (meetup, conference, etc.)
            tenant_id: Tenant ID
            status: Event status filter
            limit: Max results
        """
        try:
            temp_event = Event()
            temp_event.event_type = event_type
            temp_event.status = status

            # Use helper method for query
            result = self._query_by_index(
                model=temp_event,
                index_name="gsi6",
                ascending=True,
                limit=limit
            )

            if not result.success:
                return result

            # Post-query filtering
            valid_events = [
                event for event in result.data
                if event.tenant_id == tenant_id and not event.is_deleted()
            ]

            return ServiceResult.success_result(valid_events)

        except Exception as e:
            return self._handle_service_exception(e, 'list_by_type', event_type=event_type)

    def list_by_group(self, group_id: str, tenant_id: str, limit: int = 50) -> ServiceResult[List[Event]]:
        """
        Get events for a group using GSI7.
        
        Args:
            group_id: Group ID
            tenant_id: Tenant ID
            limit: Max results
        """
        try:
            temp_event = Event()
            temp_event.group_id = group_id

            result = self._query_by_index(
                temp_event,
                "gsi7",
                ascending=False,
                limit=limit
            )

            if not result.success:
                return result

            # Filter tenant and deleted
            active_events = []
            for event in result.data:
                if not event.is_deleted() and event.tenant_id == tenant_id:
                    active_events.append(event)

            return ServiceResult.success_result(active_events)

        except Exception as e:
            return self._handle_service_exception(e, 'list_by_group', group_id=group_id)

    def list_public_events(self, tenant_id: str, visibility: str = 'public',
                          status: str = 'published', limit: int = 50) -> ServiceResult[List[Event]]:
        """
        Get public published events using GSI8 (discovery feed).
        
        Args:
            tenant_id: Tenant ID
            visibility: Visibility filter (public, private, members_only)
            status: Status filter (published, draft, etc.)
            limit: Max results
        """
        try:
            temp_event = Event()
            temp_event.visibility = visibility
            temp_event.status = status

            # Use helper method for query
            result = self._query_by_index(
                model=temp_event,
                index_name="gsi8",
                ascending=True,  # Upcoming first
                limit=limit
            )

            if not result.success:
                return result

            # Post-query filtering
            valid_events = [
                event for event in result.data
                if event.tenant_id == tenant_id and not event.is_deleted()
            ]

            return ServiceResult.success_result(valid_events)

        except Exception as e:
            return self._handle_service_exception(e, 'list_public_events', visibility=visibility, status=status)

    def list_by_tenant(self, tenant_id: str, user_id: str = None, limit: int = 50) -> ServiceResult[List[Event]]:
        """
        Get all events for a tenant using GSI5.
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID (optional, for access control)
            limit: Max results
        """
        try:
            temp_event = Event()
            temp_event.tenant_id = tenant_id

            result = self._query_by_index(
                temp_event,
                "gsi5",
                ascending=False,
                limit=limit
            )

            if not result.success:
                return result

            # Filter deleted
            active_events = []
            for event in result.data:
                if not event.is_deleted():
                    active_events.append(event)

            return ServiceResult.success_result(active_events)

        except Exception as e:
            return self._handle_service_exception(e, 'list_by_tenant', tenant_id=tenant_id)

    def update(self, resource_id: str, tenant_id: str, user_id: str,
               updates: Dict[str, Any]) -> ServiceResult[Event]:
        """
        Update event with access control.
        
        Args:
            resource_id: Event ID
            tenant_id: Tenant ID
            user_id: User making update
            updates: Fields to update
        """
        try:
            # Get existing event
            event = self._get_model_by_id(resource_id, Event)

            if not event:
                raise NotFoundError(f"Event with ID {resource_id} not found")

            # Validate tenant access
            if hasattr(event, 'tenant_id'):
                self._validate_tenant_access(event.tenant_id, tenant_id)

            # Check permissions (owner or host)
            if not (event.owner_id == user_id or self._is_host(resource_id, user_id, tenant_id)):
                raise AccessDeniedError("Access denied: only event owner/hosts can update")

            # Handle datetime conversions
            if 'start_datetime' in updates and 'start_utc_ts' not in updates:
                updates['start_utc_ts'] = Event.datetime_to_utc_ts(updates['start_datetime'])
            if 'end_datetime' in updates and 'end_utc_ts' not in updates:
                updates['end_utc_ts'] = Event.datetime_to_utc_ts(updates['end_datetime'])

            # Validate dates if updating
            if 'start_utc_ts' in updates:
                if event.status != 'draft' and updates['start_utc_ts'] < dt.datetime.now(dt.UTC).timestamp():
                    raise ValidationError("Event start time must be in the future")
            
            # Block group_id changes after creation
            if 'group_id' in updates and event.group_id and updates['group_id'] != event.group_id:
                raise ValidationError("Cannot change group_id after event creation")

            # Apply updates using map()
            event = event.map(updates)
            
            # Update metadata
            event.updated_by_id = user_id
            event.prep_for_save()

            # Save
            return self._save_model(event)

        except Exception as e:
            return self._handle_service_exception(e, 'update_event', resource_id=resource_id)

    def delete(self, resource_id: str, tenant_id: str, user_id: str) -> ServiceResult[bool]:
        """
        Soft delete event with access control.
        
        Args:
            resource_id: Event ID
            tenant_id: Tenant ID
            user_id: User deleting event
        """
        try:
            event = self._get_model_by_id(resource_id, Event)

            if not event:
                raise NotFoundError(f"Event with ID {resource_id} not found")

            if event.is_deleted():
                return ServiceResult.success_result(True)

            # Validate tenant
            if hasattr(event, 'tenant_id'):
                self._validate_tenant_access(event.tenant_id, tenant_id)

            # Check permissions
            if not (event.owner_id == user_id or self._is_host(resource_id, user_id, tenant_id)):
                raise AccessDeniedError("Access denied: only event owner/hosts can delete")

            # Soft delete
            event.deleted_utc_ts = dt.datetime.now(dt.UTC).timestamp()
            event.deleted_by_id = user_id
            event.prep_for_save()

            save_result = self._save_model(event)
            return ServiceResult.success_result(save_result.success) if save_result.success else save_result

        except Exception as e:
            return self._handle_service_exception(e, 'delete_event', resource_id=resource_id)

    def publish(self, resource_id: str, tenant_id: str, user_id: str) -> ServiceResult[Event]:
        """
        Publish a draft event.
        
        Args:
            resource_id: Event ID
            tenant_id: Tenant ID
            user_id: User publishing
        """
        try:
            return self.update(resource_id, tenant_id, user_id, {'status': 'published'})
        except Exception as e:
            return self._handle_service_exception(e, 'publish_event', resource_id=resource_id)

    def cancel(self, resource_id: str, tenant_id: str, user_id: str,
               cancellation_reason: str = None) -> ServiceResult[Event]:
        """
        Cancel an event.
        
        Args:
            resource_id: Event ID
            tenant_id: Tenant ID
            user_id: User cancelling
            cancellation_reason: Reason for cancellation
        """
        try:
            updates = {'status': 'cancelled'}
            if cancellation_reason:
                updates['cancellation_reason'] = cancellation_reason
            
            return self.update(resource_id, tenant_id, user_id, updates)
        except Exception as e:
            return self._handle_service_exception(e, 'cancel_event', resource_id=resource_id)

    def create_draft(self, tenant_id: str, user_id: str, **kwargs) -> ServiceResult[Event]:
        """
        Create a draft event with minimal required fields.
        Auto-generates a future date if not provided.
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID
            **kwargs: Optional event fields
        """
        # Ensure status is draft
        kwargs['status'] = 'draft'
        
        # Auto-generate start date if not provided (1 week from now)
        if not kwargs.get('start_utc_ts') and not kwargs.get('start_datetime') and not kwargs.get('date'):
            future_date = dt.datetime.now(dt.UTC) + dt.timedelta(days=7)
            kwargs['start_utc_ts'] = future_date.timestamp()
        
        # Use the standard create method (draft events don't require date validation)
        return self.create(tenant_id, user_id, **kwargs)

    def get_events_by_organizer(self, organizer_id: str, tenant_id: str, user_id: str, 
                                limit: int = 50) -> ServiceResult[List[Event]]:
        """
        Get events by organizer ID (uses owner_id field).
        Alias for list_by_owner for backward compatibility.
        
        Args:
            organizer_id: Organizer user ID
            tenant_id: Tenant ID
            user_id: Requesting user ID
            limit: Max results
        """
        return self.list_by_owner(organizer_id, tenant_id, limit)

    def get_events_by_group(self, group_id: str, tenant_id: str, user_id: str,
                           limit: int = 50) -> ServiceResult[List[Event]]:
        """
        Get events by group ID.
        Wrapper for list_by_group for backward compatibility.
        
        Args:
            group_id: Group ID
            tenant_id: Tenant ID
            user_id: Requesting user ID
            limit: Max results
        """
        return self.list_by_group(group_id, tenant_id, limit)

    def get_upcoming_events(self, tenant_id: str, user_id: str, limit: int = 50) -> ServiceResult[List[Event]]:
        """
        Get upcoming events for a tenant (events starting in the future).
        
        Args:
            tenant_id: Tenant ID
            user_id: Requesting user ID
            limit: Max results
        """
        try:
            # Get all events for tenant
            result = self.list_by_tenant(tenant_id, limit=limit)
            
            if not result.success:
                return result
            
            # Filter to only upcoming events
            now_ts = dt.datetime.now(dt.UTC).timestamp()
            upcoming_events = [
                event for event in result.data 
                if event.start_utc_ts and event.start_utc_ts > now_ts
            ]
            
            # Sort by start date (soonest first)
            upcoming_events.sort(key=lambda e: e.start_utc_ts or 0)
            
            return ServiceResult.success_result(upcoming_events)
            
        except Exception as e:
            return self._handle_service_exception(e, 'get_upcoming_events', tenant_id=tenant_id)

    # Helper Methods
    def _is_host(self, event_id: str, user_id: str, tenant_id: str) -> bool:
        """Check if user is a host (organizer or co-host) for event."""
        try:
            from .event_attendee_service import EventAttendeeService
            attendee_service = EventAttendeeService(dynamodb=self.dynamodb, table_name=self.table_name)
            
            result = attendee_service.get_attendee(event_id, user_id, tenant_id)
            if result.success:
                return result.data.is_host()
            return False
        except:
            return False

    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates in kilometers (Haversine formula)."""
        R = 6371  # Earth's radius in km

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)

        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c
