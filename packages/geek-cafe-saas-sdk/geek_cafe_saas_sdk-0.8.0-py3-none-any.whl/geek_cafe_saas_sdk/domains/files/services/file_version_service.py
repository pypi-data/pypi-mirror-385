"""
FileVersionService for explicit file version management.

Geek Cafe, LLC
MIT License. See Project Root for the license information.
"""

from typing import Dict, Any, Optional, List
from boto3.dynamodb.conditions import Key
from boto3_assist.dynamodb.dynamodb import DynamoDB
from boto3_assist.dynamodb.dynamodb_index import DynamoDBKey
from geek_cafe_saas_sdk.services.database_service import DatabaseService
from geek_cafe_saas_sdk.core.service_result import ServiceResult
from geek_cafe_saas_sdk.core.service_errors import ValidationError, NotFoundError, AccessDeniedError
from geek_cafe_saas_sdk.core.error_codes import ErrorCode
from geek_cafe_saas_sdk.domains.files.models.file_version import FileVersion
from geek_cafe_saas_sdk.domains.files.models.file import File
from geek_cafe_saas_sdk.domains.files.services.s3_file_service import S3FileService
import datetime as dt
import os


class FileVersionService(DatabaseService[FileVersion]):
    """
    File version service for explicit version management.
    
    Handles:
    - Creating new versions of files
    - Version history listing
    - Version restoration
    - Version comparison
    - Version cleanup (retention policy)
    """
    
    def __init__(
        self,
        *,
        dynamodb: Optional[DynamoDB] = None,
        table_name: Optional[str] = None,
        s3_service: Optional[S3FileService] = None,
        default_bucket: Optional[str] = None,
        max_versions: Optional[int] = None,
        request_context: Optional[Dict[str, str]] = None
    ):
        """
        Initialize FileVersionService.
        
        Args:
            dynamodb: DynamoDB instance
            table_name: DynamoDB table name
            s3_service: S3FileService instance
            default_bucket: Default S3 bucket
            max_versions: Maximum versions to retain (default: 25)
        """
        super().__init__(dynamodb=dynamodb, table_name=table_name, request_context=request_context)
        self.s3_service = s3_service or S3FileService(default_bucket=default_bucket)
        self.default_bucket = default_bucket or os.getenv("S3_FILE_BUCKET")
        self.max_versions = max_versions or int(os.getenv("FILE_MAX_VERSIONS", "25"))
    
    def create(
        self,
        tenant_id: str,
        user_id: str,
        file_id: str,
        file_data: bytes,
        change_description: Optional[str] = None,
        **kwargs
    ) -> ServiceResult[FileVersion]:
        """
        Create a new version of a file.
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID (who is creating the version)
            file_id: File ID
            file_data: New file content bytes
            change_description: Optional description of changes
            
        Returns:
            ServiceResult with FileVersion model
        """
        try:
            # Get the original file
            file_result = self._get_file(tenant_id, file_id, user_id)
            if not file_result.success:
                return file_result
            
            file = file_result.data
            
            # Verify file uses explicit versioning
            if file.versioning_strategy != "explicit":
                raise ValidationError(
                    "File does not use explicit versioning strategy",
                    "versioning_strategy"
                )
            
            # Get current version number from file metadata (more reliable than GSI query)
            current_version_num = file.version_count or 0
            new_version_num = current_version_num + 1
            
            # Create FileVersion model
            version = FileVersion()
            version.tenant_id = tenant_id
            version.file_id = file_id
            version.version_number = new_version_num
            version.created_by = user_id
            version.change_description = change_description
            version.file_size = len(file_data)
            version.mime_type = file.mime_type
            version.checksum = self._calculate_checksum(file_data)
            version.is_current = True
            version.status = "active"
            
            # Must call prep_for_save before accessing version_id
            version.prep_for_save()
            
            # Build S3 key for this version
            s3_key = f"{tenant_id}/files/{file_id}/versions/{version.version_id}/{file.file_name}"
            version.s3_bucket = self.default_bucket
            version.s3_key = s3_key
            
            # Upload to S3
            upload_result = self.s3_service.upload_file(
                file_data=file_data,
                key=s3_key,
                bucket=self.default_bucket
            )
            
            if not upload_result.success:
                return ServiceResult.error_result(
                    message=f"Failed to upload version to S3: {upload_result.message}",
                    error_code=upload_result.error_code
                )
            
            # Mark previous version as not current
            if file.current_version_id:
                self._mark_version_as_not_current(tenant_id, file_id, file.current_version_id)
            
            # Save version metadata to DynamoDB (already called prep_for_save above)
            save_result = self._save_model(version)
            
            if not save_result.success:
                return save_result
            
            # Update file record with new current version
            self._update_file_current_version(
                tenant_id,
                file_id,
                version.version_id,
                new_version_num
            )
            
            # Apply retention policy
            self._apply_retention_policy(tenant_id, file_id)
            
            return ServiceResult.success_result(version)
            
        except ValidationError as e:
            return ServiceResult.error_result(
                message=str(e),
                error_code=ErrorCode.VALIDATION_ERROR
            )
        except Exception as e:
            return ServiceResult.exception_result(
                exception=e,
                error_code=ErrorCode.INTERNAL_ERROR,
                context="FileVersionService.create"
            )
    
    def get_by_id(
        self,
        resource_id: str,
        tenant_id: str,
        user_id: str,
        file_id: Optional[str] = None
    ) -> ServiceResult[FileVersion]:
        """
        Get version by ID with access control.
        
        Args:
            resource_id: Version ID
            tenant_id: Tenant ID
            user_id: User ID (for access control)
            file_id: File ID (required if version_id alone is ambiguous)
            
        Returns:
            ServiceResult with FileVersion model
        """
        try:
            # Use helper method with tenant check
            version = self._get_model_by_id_with_tenant_check(resource_id, FileVersion, tenant_id)
            
            if not version:
                raise NotFoundError(f"Version not found: {resource_id}")
            
            # Access control: Check file ownership
            if file_id:
                file_result = self._get_file(tenant_id, file_id, user_id)
                if not file_result.success:
                    raise AccessDeniedError("You do not have access to this file version")
            else:
                # If no file_id provided, check using version's file_id
                file_result = self._get_file(tenant_id, version.file_id, user_id)
                if not file_result.success:
                    raise AccessDeniedError("You do not have access to this file version")
            
            return ServiceResult.success_result(version)
            
        except (NotFoundError, ValidationError) as e:
            return ServiceResult.error_result(
                message=str(e),
                error_code=ErrorCode.NOT_FOUND if isinstance(e, NotFoundError) else ErrorCode.VALIDATION_ERROR
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
                context="FileVersionService.get_by_id"
            )
    
    def update(
        self,
        resource_id: str,
        tenant_id: str,
        user_id: str,
        updates: Dict[str, Any]
    ) -> ServiceResult[FileVersion]:
        """
        Update version metadata (limited fields).
        
        Args:
            resource_id: Version ID
            tenant_id: Tenant ID
            user_id: User ID (for access control)
            updates: Dictionary of fields to update
            
        Returns:
            ServiceResult with updated FileVersion model
        """
        try:
            # Get file_id from updates if provided
            file_id = updates.get('file_id')
            if not file_id:
                raise ValidationError("file_id is required in updates", "file_id")
            
            # Get existing version
            get_result = self.get_by_id(resource_id, tenant_id, user_id, file_id=file_id)
            if not get_result.success:
                return get_result
            
            version = get_result.data
            
            # Only allow updating change_description and status
            allowed_fields = ["change_description", "status"]
            
            for field, value in updates.items():
                if field in allowed_fields:
                    setattr(version, field, value)
            
            # Update timestamp
            version.updated_utc_ts = dt.datetime.now(dt.UTC).timestamp()
            
            # Save to DynamoDB
            version.prep_for_save()
            return self._save_model(version)
            
        except (ValidationError, AccessDeniedError) as e:
            return ServiceResult.error_result(
                message=str(e),
                error_code=ErrorCode.VALIDATION_ERROR if isinstance(e, ValidationError) else ErrorCode.ACCESS_DENIED
            )
        except Exception as e:
            return ServiceResult.exception_result(
                exception=e,
                error_code=ErrorCode.INTERNAL_ERROR,
                context="FileVersionService.update"
            )
    
    def delete(
        self,
        resource_id: str,
        tenant_id: str,
        user_id: str,
        file_id: str
    ) -> ServiceResult[bool]:
        """
        Delete a version (cannot delete current version).
        
        Args:
            resource_id: Version ID
            tenant_id: Tenant ID
            user_id: User ID (for access control)
            file_id: File ID
            
        Returns:
            ServiceResult with success boolean
        """
        try:
            # Get existing version
            get_result = self.get_by_id(resource_id, tenant_id, user_id, file_id=file_id)
            if not get_result.success:
                return get_result
            
            version = get_result.data
            
            # Cannot delete current version
            if version.is_current:
                raise ValidationError(
                    "Cannot delete the current version. Restore a different version first.",
                    "is_current"
                )
            
            # Soft delete - mark as archived
            version.status = "archived"
            version.deleted_utc_ts = dt.datetime.now(dt.UTC).timestamp()
            
            version.prep_for_save()
            save_result = self._save_model(version)
            
            if not save_result.success:
                return save_result
            
            # Note: S3 file is kept for potential recovery
            
            return ServiceResult.success_result(True)
            
        except ValidationError as e:
            return ServiceResult.error_result(
                message=str(e),
                error_code=ErrorCode.VALIDATION_ERROR
            )
        except Exception as e:
            return ServiceResult.exception_result(
                exception=e,
                error_code=ErrorCode.INTERNAL_ERROR,
                context="FileVersionService.delete"
            )
    
    def list_versions(
        self,
        tenant_id: str,
        file_id: str,
        user_id: str,
        limit: int = 50
    ) -> ServiceResult[List[FileVersion]]:
        """
        List all versions of a file.
        
        Args:
            tenant_id: Tenant ID
            file_id: File ID
            user_id: User ID (for access control)
            limit: Maximum number of results
            
        Returns:
            ServiceResult with list of FileVersion models
        """
        try:
            # Check file access
            file_result = self._get_file(tenant_id, file_id, user_id)
            if not file_result.success:
                return ServiceResult.error_result(
                    message="File not found or access denied",
                    error_code=ErrorCode.ACCESS_DENIED
                )
            
            # Use GSI1 to query versions by file
            gsi1_pk = DynamoDBKey.build_key(("file", file_id))
            
            # Query using boto3_assist DynamoDB query
            results = self.dynamodb.query(
                key=Key("gsi1_pk").eq(gsi1_pk),
                table_name=self.table_name,
                index_name="gsi1",
                ascending=False,  # Descending order (newest first)
                limit=limit
            )
            
            # Map results to FileVersion models
            versions = []
            if results and 'Items' in results:
                for item in results['Items']:
                    version = FileVersion()
                    version.map(item)
                    # Filter out archived versions (which includes deleted ones)
                    if version.status == "active":
                        versions.append(version)
            
            return ServiceResult.success_result(versions)
            
        except Exception as e:
            return ServiceResult.exception_result(
                exception=e,
                error_code=ErrorCode.INTERNAL_ERROR,
                context="FileVersionService.list_versions"
            )
    
    def restore_version(
        self,
        tenant_id: str,
        file_id: str,
        version_id: str,
        user_id: str
    ) -> ServiceResult[FileVersion]:
        """
        Restore a previous version as the current version.
        
        Args:
            tenant_id: Tenant ID
            file_id: File ID
            version_id: Version ID to restore
            user_id: User ID
            
        Returns:
            ServiceResult with restored FileVersion (now current)
        """
        try:
            # Get the version to restore
            get_result = self.get_by_id(version_id, tenant_id, user_id, file_id=file_id)
            if not get_result.success:
                return get_result
            
            version_to_restore = get_result.data
            
            # Get file
            file_result = self._get_file(tenant_id, file_id, user_id)
            if not file_result.success:
                return file_result
            
            file = file_result.data
            
            # Mark current version as not current
            if file.current_version_id:
                self._mark_version_as_not_current(tenant_id, file_id, file.current_version_id)
            
            # Mark restored version as current
            version_to_restore.is_current = True
            version_to_restore.updated_utc_ts = dt.datetime.now(dt.UTC).timestamp()
            
            version_to_restore.prep_for_save()
            save_result = self._save_model(version_to_restore)
            
            if not save_result.success:
                return save_result
            
            # Update file record
            self._update_file_current_version(
                tenant_id,
                file_id,
                version_id,
                version_to_restore.version_number
            )
            
            return ServiceResult.success_result(version_to_restore)
            
        except Exception as e:
            return ServiceResult.exception_result(
                exception=e,
                error_code=ErrorCode.INTERNAL_ERROR,
                context="FileVersionService.restore_version"
            )
    
    def download_version(
        self,
        tenant_id: str,
        file_id: str,
        version_id: str,
        user_id: str
    ) -> ServiceResult[Dict[str, Any]]:
        """
        Download a specific version of a file.
        
        Args:
            tenant_id: Tenant ID
            file_id: File ID
            version_id: Version ID
            user_id: User ID
            
        Returns:
            ServiceResult with file data and metadata
        """
        try:
            # Get version
            get_result = self.get_by_id(version_id, tenant_id, user_id, file_id=file_id)
            if not get_result.success:
                return get_result
            
            version = get_result.data
            
            # Download from S3
            download_result = self.s3_service.download_file(
                key=version.s3_key,
                bucket=version.s3_bucket
            )
            
            if not download_result.success:
                return ServiceResult.error_result(
                    message=f"Failed to download version from S3: {download_result.message}",
                    error_code=download_result.error_code
                )
            
            return ServiceResult.success_result({
                "version": version,
                "data": download_result.data["data"],
                "content_type": download_result.data.get("content_type", version.mime_type),
                "size": download_result.data.get("size", version.file_size)
            })
            
        except Exception as e:
            return ServiceResult.exception_result(
                exception=e,
                error_code=ErrorCode.INTERNAL_ERROR,
                context="FileVersionService.download_version"
            )
    
    # Helper methods
    
    def _get_file(self, tenant_id: str, file_id: str, user_id: str) -> ServiceResult[File]:
        """Get file with access control."""
        try:
            # Use DatabaseService helper to get file
            file = self._get_model_by_id_with_tenant_check(file_id, File, tenant_id)
            
            if not file:
                raise NotFoundError(f"File not found: {file_id}")
            
            if file.owner_id != user_id:
                raise AccessDeniedError("You do not have access to this file")
            
            return ServiceResult.success_result(file)
            
        except (NotFoundError, AccessDeniedError) as e:
            return ServiceResult.error_result(
                message=str(e),
                error_code=ErrorCode.NOT_FOUND if isinstance(e, NotFoundError) else ErrorCode.ACCESS_DENIED
            )
    
    def _get_latest_version_number(self, tenant_id: str, file_id: str) -> int:
        """Get the latest version number for a file."""
        try:
            # Query versions for this file using DatabaseService helper
            temp_version = FileVersion()
            temp_version.file_id = file_id
            
            result = self._query_by_index(temp_version, "gsi1", limit=1, ascending=False)
            
            if result.success and result.data:
                return result.data[0].version_number
            
            return 0  # No versions yet
            
        except Exception:
            return 0
    
    def _mark_version_as_not_current(
        self,
        tenant_id: str,
        file_id: str,
        version_id: str
    ) -> None:
        """Mark a version as not current."""
        try:
            # Use DatabaseService helper to get version
            version = self._get_model_by_id_with_tenant_check(version_id, FileVersion, tenant_id)
            
            if version:
                version.is_current = False
                
                version.prep_for_save()
                self._save_model(version)
        except Exception:
            pass  # Best effort
    
    def _update_file_current_version(
        self,
        tenant_id: str,
        file_id: str,
        version_id: str,
        version_number: int
    ) -> None:
        """Update file record with current version info."""
        try:
            # Use DatabaseService helper to get the file (uses primary key)
            file = self._get_model_by_id_with_tenant_check(file_id, File, tenant_id)
            
            if file:
                file.current_version_id = version_id
                file.version_count = version_number
                file.updated_utc_ts = dt.datetime.now(dt.UTC).timestamp()
                
                file.prep_for_save()
                self._save_model(file)
        except Exception:
            pass  # Best effort
    
    def _apply_retention_policy(self, tenant_id: str, file_id: str) -> None:
        """Apply version retention policy (delete old versions beyond max_versions)."""
        try:
            # Get all versions
            gsi1_pk = DynamoDBKey.build_key(("file", file_id))
            
            results = self.dynamodb.query(
                key=Key("gsi1_pk").eq(gsi1_pk),
                table_name=self.table_name,
                index_name="gsi1",
                ascending=False  # Descending order (newest first)
            )
            
            items = results.get('Items', [])
            active_versions = [item for item in items if item.get('status') == 'active']
            
            # If we exceed max_versions, mark old ones as archived
            if len(active_versions) > self.max_versions:
                versions_to_archive = active_versions[self.max_versions:]
                
                for item in versions_to_archive:
                    version = FileVersion()
                    version.map(item)
                    
                    if not version.is_current:  # Never archive current version
                        version.status = "archived"
                        version.updated_utc_ts = dt.datetime.now(dt.UTC).timestamp()
                        
                        version.prep_for_save()
                        self._save_model(version)
        except Exception:
            pass  # Best effort
    
    def _calculate_checksum(self, data: bytes) -> str:
        """Calculate checksum for file data."""
        import hashlib
        return hashlib.sha256(data).hexdigest()
