"""
DirectoryService for virtual directory hierarchy management.

Geek Cafe, LLC
MIT License. See Project Root for the license information.
"""

from typing import Dict, Any, Optional, List
from boto3.dynamodb.conditions import Key
from boto3_assist.dynamodb.dynamodb import DynamoDB
from geek_cafe_saas_sdk.services.database_service import DatabaseService
from geek_cafe_saas_sdk.core.service_result import ServiceResult
from geek_cafe_saas_sdk.core.service_errors import ValidationError, NotFoundError, AccessDeniedError
from geek_cafe_saas_sdk.core.error_codes import ErrorCode
from geek_cafe_saas_sdk.domains.files.models.directory import Directory
import datetime as dt


class DirectoryService(DatabaseService[Directory]):
    """
    Directory service for managing virtual directory hierarchy.
    
    Handles:
    - Directory creation and deletion
    - Hierarchy traversal
    - Path resolution
    - Directory statistics (file count, size)
    - Move/rename operations
    """
    
    def create(
        self,
        tenant_id: str,
        user_id: str,
        directory_name: str,
        parent_id: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
        **kwargs
    ) -> ServiceResult[Directory]:
        """
        Create a new directory.
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID (directory owner)
            directory_name: Directory name
            parent_id: Optional parent directory ID
            description: Optional description
            color: Optional color code
            icon: Optional icon name
            
        Returns:
            ServiceResult with Directory model
        """
        try:
            # Validate inputs
            if not directory_name or not directory_name.strip():
                raise ValidationError("Directory name is required", "directory_name")
            
            # Validate directory name (no special chars)
            if '/' in directory_name or '\\' in directory_name:
                raise ValidationError(
                    "Directory name cannot contain slashes",
                    "directory_name"
                )
            
            # If parent specified, verify it exists
            parent_dir = None
            if parent_id:
                parent_result = self.get_by_id(parent_id, tenant_id, user_id)
                if not parent_result.success:
                    return ServiceResult.error_result(
                        message=f"Parent directory not found: {parent_id}",
                        error_code=ErrorCode.NOT_FOUND
                    )
                parent_dir = parent_result.data
            
            # Check for duplicate name in same parent
            duplicate_check = self._check_duplicate_name(
                tenant_id, directory_name, parent_id
            )
            if duplicate_check:
                raise ValidationError(
                    f"Directory '{directory_name}' already exists in this location",
                    "directory_name"
                )
            
            # Create Directory model
            directory = Directory()
            directory.prep_for_save()
            directory.tenant_id = tenant_id
            directory.owner_id = user_id
            directory.directory_name = directory_name
            directory.parent_id = parent_id
            directory.description = description
            directory.color = color
            directory.icon = icon
            directory.status = "active"
            
            # Calculate depth and full path
            if parent_dir:
                directory.depth = parent_dir.depth + 1
                directory.full_path = f"{parent_dir.full_path}/{directory_name}"
            else:
                directory.depth = 0
                directory.full_path = f"/{directory_name}"
            
            # Initialize counters
            directory.file_count = 0
            directory.subdirectory_count = 0
            directory.total_size = 0
            
            # Save to DynamoDB
            directory.prep_for_save()
            save_result = self._save_model(directory)
            
            if not save_result.success:
                return save_result
            
            # Update parent's subdirectory count
            if parent_id:
                self._increment_subdirectory_count(tenant_id, parent_id, 1)
            
            return ServiceResult.success_result(directory)
            
        except ValidationError as e:
            return ServiceResult.error_result(
                message=str(e),
                error_code=ErrorCode.VALIDATION_ERROR
            )
        except Exception as e:
            return ServiceResult.exception_result(
                exception=e,
                error_code=ErrorCode.INTERNAL_ERROR,
                context="DirectoryService.create"
            )
    
    def get_by_id(
        self,
        resource_id: str,
        tenant_id: str,
        user_id: str
    ) -> ServiceResult[Directory]:
        """
        Get directory by ID with access control.
        
        Args:
            resource_id: Directory ID
            tenant_id: Tenant ID
            user_id: User ID (for access control)
            
        Returns:
            ServiceResult with Directory model
        """
        try:
            # Use helper method with tenant check
            directory = self._get_model_by_id_with_tenant_check(resource_id, Directory, tenant_id)
            
            # Check if directory exists
            if not directory:
                raise NotFoundError(f"Directory not found: {resource_id}")
            
            # Access control: Check if user is owner
            if directory.owner_id != user_id:
                # TODO: Check shared access
                raise AccessDeniedError("You do not have access to this directory")
            
            return ServiceResult.success_result(directory)
            
        except NotFoundError as e:
            return ServiceResult.error_result(
                message=str(e),
                error_code=ErrorCode.NOT_FOUND
            )
        except AccessDeniedError as e:
            return ServiceResult.error_result(
                message=str(e),
                error_code=ErrorCode.ACCESS_DENIED
            )
        except Exception as e:
            return ServiceResult.exception_result(
                exception=e,
                error_code=ErrorCode.INTERNAL_ERROR,
                context="DirectoryService.get_by_id"
            )
    
    def update(
        self,
        resource_id: str,
        tenant_id: str,
        user_id: str,
        updates: Dict[str, Any]
    ) -> ServiceResult[Directory]:
        """
        Update directory metadata.
        
        Args:
            resource_id: Directory ID
            tenant_id: Tenant ID
            user_id: User ID (for access control)
            updates: Dictionary of fields to update
            
        Returns:
            ServiceResult with updated Directory model
        """
        try:
            # Get existing directory
            get_result = self.get_by_id(resource_id, tenant_id, user_id)
            if not get_result.success:
                return get_result
            
            directory = get_result.data
            
            # Only owner can update
            if directory.owner_id != user_id:
                raise AccessDeniedError("Only the owner can update this directory")
            
            # Apply updates (only allowed fields)
            allowed_fields = [
                "directory_name", "description", "color", "icon", "status"
            ]
            
            # Handle directory rename
            if "directory_name" in updates:
                new_name = updates["directory_name"]
                if not new_name or not new_name.strip():
                    raise ValidationError("Directory name cannot be empty", "directory_name")
                
                if '/' in new_name or '\\' in new_name:
                    raise ValidationError(
                        "Directory name cannot contain slashes",
                        "directory_name"
                    )
                
                # Check for duplicate
                if new_name != directory.directory_name:
                    duplicate = self._check_duplicate_name(
                        tenant_id, new_name, directory.parent_id
                    )
                    if duplicate:
                        raise ValidationError(
                            f"Directory '{new_name}' already exists in this location",
                            "directory_name"
                        )
                    
                    # Update full path
                    old_path = directory.full_path
                    if directory.parent_id:
                        # Get parent path
                        parent_result = self.get_by_id(directory.parent_id, tenant_id, user_id)
                        if parent_result.success:
                            directory.full_path = f"{parent_result.data.full_path}/{new_name}"
                    else:
                        directory.full_path = f"/{new_name}"
                    
                    directory.directory_name = new_name
            
            # Apply other updates
            for field, value in updates.items():
                if field in allowed_fields and field != "directory_name":
                    setattr(directory, field, value)
            
            # Update timestamp
            directory.updated_utc_ts = dt.datetime.now(dt.UTC).timestamp()
            
            # Call prep_for_save() AFTER all properties are set
            # This ensures GSI lambdas evaluate with the updated values
            directory.prep_for_save()
            
            # Save to DynamoDB
            return self._save_model(directory)
            
        except (ValidationError, AccessDeniedError) as e:
            return ServiceResult.error_result(
                message=str(e),
                error_code=ErrorCode.VALIDATION_ERROR if isinstance(e, ValidationError) else ErrorCode.ACCESS_DENIED
            )
        except Exception as e:
            return ServiceResult.exception_result(
                exception=e,
                error_code=ErrorCode.INTERNAL_ERROR,
                context="DirectoryService.update"
            )
    
    def delete(
        self,
        resource_id: str,
        tenant_id: str,
        user_id: str,
        recursive: bool = False
    ) -> ServiceResult[bool]:
        """
        Delete directory.
        
        Args:
            resource_id: Directory ID
            tenant_id: Tenant ID
            user_id: User ID (for access control)
            recursive: If True, delete subdirectories and files. If False, fail if not empty.
            
        Returns:
            ServiceResult with success boolean
        """
        try:
            # Get existing directory
            get_result = self.get_by_id(resource_id, tenant_id, user_id)
            if not get_result.success:
                return get_result
            
            directory = get_result.data
            
            # Only owner can delete
            if directory.owner_id != user_id:
                raise AccessDeniedError("Only the owner can delete this directory")
            
            # Check if directory is empty
            if not recursive and (directory.file_count > 0 or directory.subdirectory_count > 0):
                raise ValidationError(
                    "Directory is not empty. Use recursive=True to delete contents.",
                    "recursive"
                )
            
            # TODO: If recursive, delete all subdirectories and files
            # For now, just soft delete the directory
            directory.status = "deleted"
            directory.deleted_utc_ts = dt.datetime.now(dt.UTC).timestamp()
            
            directory.prep_for_save()
            save_result = self._save_model(directory)
            
            if not save_result.success:
                return save_result
            
            # Update parent's subdirectory count
            if directory.parent_id:
                self._increment_subdirectory_count(tenant_id, directory.parent_id, -1)
            
            return ServiceResult.success_result(True)
            
        except (ValidationError, AccessDeniedError) as e:
            return ServiceResult.error_result(
                message=str(e),
                error_code=ErrorCode.VALIDATION_ERROR if isinstance(e, ValidationError) else ErrorCode.ACCESS_DENIED
            )
        except Exception as e:
            return ServiceResult.exception_result(
                exception=e,
                error_code=ErrorCode.INTERNAL_ERROR,
                context="DirectoryService.delete"
            )
    
    def list_subdirectories(
        self,
        tenant_id: str,
        parent_id: Optional[str],
        user_id: str,
        limit: int = 50
    ) -> ServiceResult[List[Directory]]:
        """
        List subdirectories in a directory.
        
        Args:
            tenant_id: Tenant ID
            parent_id: Parent directory ID (None for root)
            user_id: User ID (for access control)
            limit: Maximum number of results
            
        Returns:
            ServiceResult with list of Directory models
        """
        try:
            # Use GSI2 to query subdirectories by parent
            temp_directory = Directory()
            temp_directory.tenant_id = tenant_id
            temp_directory.parent_id = parent_id  # None for root directories
            
            # Query using helper method
            query_result = self._query_by_index(temp_directory, "gsi2", limit=limit, ascending=True)
            
            if not query_result.success:
                return query_result
            
            # Filter results
            directories = []
            for directory in query_result.data:
                # Debug: print what we're seeing
                # print(f"Found dir: {directory.directory_name}, parent_id={directory.parent_id}, expected={parent_id}")
                # Filter out deleted directories and apply access control
                if directory.status != "deleted" and directory.owner_id == user_id:
                    # Only include directories whose parent_id matches what we're looking for
                    if directory.parent_id == parent_id:
                        directories.append(directory)
            
            return ServiceResult.success_result(directories)
            
        except Exception as e:
            return ServiceResult.exception_result(
                exception=e,
                error_code=ErrorCode.INTERNAL_ERROR,
                context="DirectoryService.list_subdirectories"
            )
    
    def get_path_components(
        self,
        directory_id: str,
        tenant_id: str,
        user_id: str
    ) -> ServiceResult[List[Directory]]:
        """
        Get all directories in the path from root to target directory.
        
        Args:
            directory_id: Target directory ID
            tenant_id: Tenant ID
            user_id: User ID
            
        Returns:
            ServiceResult with list of Directory models (root to target)
        """
        try:
            path = []
            current_id = directory_id
            
            # Traverse up to root
            while current_id:
                result = self.get_by_id(current_id, tenant_id, user_id)
                if not result.success:
                    return result
                
                directory = result.data
                path.insert(0, directory)  # Prepend to build root-to-target order
                current_id = directory.parent_id
            
            return ServiceResult.success_result(path)
            
        except Exception as e:
            return ServiceResult.exception_result(
                exception=e,
                error_code=ErrorCode.INTERNAL_ERROR,
                context="DirectoryService.get_path_components"
            )
    
    def move_directory(
        self,
        directory_id: str,
        new_parent_id: Optional[str],
        tenant_id: str,
        user_id: str
    ) -> ServiceResult[Directory]:
        """
        Move directory to a new parent.
        
        Args:
            directory_id: Directory to move
            new_parent_id: New parent directory ID (None for root)
            tenant_id: Tenant ID
            user_id: User ID
            
        Returns:
            ServiceResult with updated Directory model
        """
        try:
            # Get directory to move
            get_result = self.get_by_id(directory_id, tenant_id, user_id)
            if not get_result.success:
                return get_result
            
            directory = get_result.data
            
            # Only owner can move
            if directory.owner_id != user_id:
                raise AccessDeniedError("Only the owner can move this directory")
            
            # Can't move to itself
            if directory_id == new_parent_id:
                raise ValidationError("Cannot move directory to itself", "new_parent_id")
            
            # Verify new parent exists and is not a descendant
            if new_parent_id:
                parent_result = self.get_by_id(new_parent_id, tenant_id, user_id)
                if not parent_result.success:
                    return ServiceResult.error_result(
                        message=f"Target parent directory not found: {new_parent_id}",
                        error_code=ErrorCode.NOT_FOUND
                    )
                
                parent = parent_result.data
                
                # Check if new parent is a descendant (would create cycle)
                if self._is_descendant(tenant_id, user_id, new_parent_id, directory_id):
                    raise ValidationError(
                        "Cannot move directory into its own subdirectory",
                        "new_parent_id"
                    )
                
                # Check for duplicate name
                duplicate = self._check_duplicate_name(
                    tenant_id, directory.directory_name, new_parent_id
                )
                if duplicate:
                    raise ValidationError(
                        f"Directory '{directory.directory_name}' already exists in target location",
                        "directory_name"
                    )
                
                # Update depth and path
                directory.depth = parent.depth + 1
                directory.full_path = f"{parent.full_path}/{directory.directory_name}"
            else:
                # Moving to root
                directory.depth = 0
                directory.full_path = f"/{directory.directory_name}"
            
            old_parent_id = directory.parent_id
            directory.parent_id = new_parent_id
            directory.updated_utc_ts = dt.datetime.now(dt.UTC).timestamp()
            
            # Call prep_for_save() AFTER all properties (parent_id, full_path) are set
            # This ensures GSI lambdas evaluate with the updated values
            directory.prep_for_save()
            
            # Save to DynamoDB
            save_result = self._save_model(directory)
            
            if not save_result.success:
                return save_result
            
            # Update parent counts
            if old_parent_id:
                self._increment_subdirectory_count(tenant_id, old_parent_id, -1)
            if new_parent_id:
                self._increment_subdirectory_count(tenant_id, new_parent_id, 1)
            
            return ServiceResult.success_result(directory)
            
        except (ValidationError, AccessDeniedError) as e:
            return ServiceResult.error_result(
                message=str(e),
                error_code=ErrorCode.VALIDATION_ERROR if isinstance(e, ValidationError) else ErrorCode.ACCESS_DENIED
            )
        except Exception as e:
            return ServiceResult.exception_result(
                exception=e,
                error_code=ErrorCode.INTERNAL_ERROR,
                context="DirectoryService.move_directory"
            )
    
    # Helper methods
    
    def _check_duplicate_name(
        self,
        tenant_id: str,
        directory_name: str,
        parent_id: Optional[str]
    ) -> bool:
        """Check if directory with this full path already exists.
        
        Args:
            tenant_id: Tenant ID
            directory_name: Name of directory to check
            parent_id: Parent directory ID (None for root)
            
        Returns:
            True if a non-deleted directory with this path exists
        """
        try:
            # Build the expected full_path for the new directory
            if parent_id:
                # Get parent to build full path
                parent = self._get_model_by_id(parent_id, Directory)
                if not parent:
                    return False  # Parent doesn't exist, can't check
                expected_full_path = f"{parent.full_path}/{directory_name}"
            else:
                # Root directory
                expected_full_path = f"/{directory_name}"
            
            # Query GSI1 by full_path to check for duplicates
            temp_directory = Directory()
            temp_directory.tenant_id = tenant_id
            temp_directory.full_path = expected_full_path
            
            query_result = self._query_by_index(temp_directory, "gsi1", limit=1)
            
            if not query_result.success:
                return False
            
            # Check if any non-deleted directories with this path exist
            for directory in query_result.data:
                if directory.status != "deleted":
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _increment_subdirectory_count(
        self,
        tenant_id: str,
        directory_id: str,
        delta: int
    ) -> None:
        """Increment or decrement subdirectory count."""
        try:
            # Get current directory using helper
            directory = self._get_model_by_id_with_tenant_check(directory_id, Directory, tenant_id)
            
            if directory:
                directory.subdirectory_count = max(0, directory.subdirectory_count + delta)
                
                directory.prep_for_save()
                self._save_model(directory)
        except Exception:
            # Silent fail - this is a best-effort update
            pass
    
    def _is_descendant(
        self,
        tenant_id: str,
        user_id: str,
        potential_descendant_id: str,
        ancestor_id: str
    ) -> bool:
        """Check if potential_descendant is a descendant of ancestor."""
        try:
            current_id = potential_descendant_id
            
            # Traverse up the tree
            while current_id:
                if current_id == ancestor_id:
                    return True
                
                result = self.get_by_id(current_id, tenant_id, user_id)
                if not result.success:
                    return False
                
                current_id = result.data.parent_id
            
            return False
            
        except Exception:
            return False
