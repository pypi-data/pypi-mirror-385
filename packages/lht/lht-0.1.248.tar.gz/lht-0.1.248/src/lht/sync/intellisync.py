"""
Intelligent Salesforce to Snowflake synchronization system.
This module provides streamlined sync operations with automatic method selection.
"""

import pandas as pd
import time
import logging
from typing import Optional, Dict, Any, Tuple, List
from snowflake.snowpark import Session

from ..util.sync_utils import (
    table_exists,
    get_last_modified_date,
    get_record_count,
    ensure_schema_exists,
    sql_execution
)

logger = logging.getLogger(__name__)


class IntelliSync:
    """
    Intelligent synchronization system that determines the best method to sync Salesforce data
    based on volume and previous sync status.
    """
    
    def __init__(self, session: Session, access_info: Dict[str, str]):
        """
        Initialize the intelligent sync system.
        
        Args:
            session: Snowflake Snowpark session
            access_info: Dictionary containing Salesforce access details
        """
        self.session = session
        self.access_info = access_info
        
        # Configuration thresholds
        self.BULK_API_THRESHOLD = 10000  # Use Bulk API for records >= this number
        self.REGULAR_API_THRESHOLD = 1000  # Use regular API for records < this number
        
    def sync_sobject(self, 
                    sobject: str, 
                    schema: str, 
                    table: str, 
                    match_field: str = 'ID',
                    force_full_sync: bool = False,
                    force_bulk_api: bool = False,
                    existing_job_id: Optional[str] = None,
                    delete_job: bool = True) -> Dict[str, Any]:
        """
        Intelligently sync a Salesforce SObject to Snowflake.
        
        Args:
            sobject: Salesforce SObject name (e.g., 'Account', 'Contact')
            schema: Snowflake schema name
            table: Snowflake table name
            match_field: Field to use for matching records (default: 'ID')
            force_full_sync: Force a full sync regardless of previous sync status
            force_bulk_api: Force use of Bulk API 2.0 instead of regular API
            existing_job_id: Optional existing Bulk API job ID to use
            delete_job: Whether to delete the Bulk API job after completion
            
        Returns:
            Dictionary containing sync results and metadata
        """
        logger.info(f"🔄 Starting intelligent sync for {sobject} -> {schema}.{table}")
        
        # Store configuration as instance attributes
        self.force_full_sync = force_full_sync
        self.force_bulk_api = force_bulk_api
        self.existing_job_id = existing_job_id
        self.delete_job = delete_job
        
        logger.debug(f"🔧 Force full sync: {self.force_full_sync}")
        logger.debug(f"🔧 Force bulk API: {self.force_bulk_api}")
        
        if existing_job_id:
            logger.debug(f"🔧 Using existing job ID: {existing_job_id}")
        
        logger.debug(f"🧹 Delete job after completion: {self.delete_job}")
        
        # Ensure schema exists before proceeding
        logger.debug(f"🔍 Ensuring schema {schema} exists...")
        if not ensure_schema_exists(self.session, schema):
            error_msg = f"Failed to ensure schema {schema} exists"
            logger.error(f"❌ {error_msg}")
            return self._create_error_result(sobject, schema, table, error_msg)
        
        # Check if table exists and get last modified date
        table_exists_flag = table_exists(self.session, schema, table)
        last_modified_date = None
        
        if table_exists_flag and not force_full_sync:
            last_modified_date = get_last_modified_date(self.session, schema, table)
            if last_modified_date:
                logger.info(f"🕒 Last Modified Date in Snowflake: {last_modified_date}")
            else:
                logger.info("🕒 No Last Modified Date found in Snowflake table")
        else:
            logger.info("🕒 Skipping Last Modified Date check (table doesn't exist or force_full_sync=True)")
                    
        # Determine sync strategy
        logger.debug("🎯 Determining sync strategy...")
        
        # Get estimated record count
        estimated_records = get_record_count(self.access_info, sobject, last_modified_date)
        logger.info(f"📊 Estimated records to sync: {estimated_records}")
        
        sync_strategy = self._determine_sync_strategy(
            sobject, table_exists_flag, last_modified_date, estimated_records
        )
        
        # Log the sync strategy details
        logger.info("🎯 Sync Strategy Details:")
        logger.info(f"   Method: {sync_strategy['method']}")
        logger.info(f"   Is Incremental: {sync_strategy['is_incremental']}")
        logger.info(f"   Estimated Records: {sync_strategy['estimated_records']}")
        if last_modified_date:
            logger.info(f"   Last Modified Date: {last_modified_date}")
        else:
            logger.info(f"   Last Modified Date: None (full sync)")
        
        # Execute sync based on strategy
        start_time = time.time()
        result = self._execute_sync_strategy(sync_strategy, sobject, schema, table, match_field)
        end_time = time.time()
        
        # Check result validity
        if result is None:
            raise Exception("_execute_sync_strategy returned None - sync failed")
        
        # Compile results
        sync_result = {
            'sobject': sobject,
            'target_table': f"{schema}.{table}",
            'sync_method': sync_strategy['method'],
            'estimated_records': sync_strategy['estimated_records'],
            'actual_records': result.get('records_processed', 0),
            'sync_duration_seconds': end_time - start_time,
            'last_modified_date': last_modified_date,
            'sync_timestamp': pd.Timestamp.now(),
            'success': result.get('success', False),
            'error': result.get('error', None)
        }
        
        logger.info(f"✅ Sync completed: {sync_result['actual_records']} records in {sync_result['sync_duration_seconds']:.2f}s")
        
        # Log final sync summary
        logger.info("📊 Final Sync Summary:")
        logger.info(f"   Method: {sync_result['sync_method']}")
        logger.info(f"   Estimated Records: {sync_result['estimated_records']}")
        logger.info(f"   Actual Records Synced: {sync_result['actual_records']}")
        logger.info(f"   Last Modified Date Used: {sync_result['last_modified_date']}")
        logger.info(f"   Duration: {sync_result['sync_duration_seconds']:.2f} seconds")
        return sync_result
    
    def _determine_sync_strategy(self, 
                               sobject: str,
                               table_exists_flag: bool, 
                               last_modified_date: Optional[pd.Timestamp],
                               estimated_records: int) -> Dict[str, Any]:
        """
        Determine the best synchronization strategy based on data volume and previous sync status.
        """
        
        logger.debug(f"🎯 Determining sync strategy for {sobject}")
        logger.debug(f"📋 Table exists: {table_exists_flag}")
        logger.debug(f"📅 Last modified date: {last_modified_date}")
        logger.debug(f"📊 Thresholds - Bulk API: {self.BULK_API_THRESHOLD}")
        logger.debug(f"🔧 Force bulk API: {self.force_bulk_api}")
        
        # Check if force_bulk_api is set
        if self.force_bulk_api:
            logger.debug("🔧 Force bulk API is enabled - using Bulk API regardless of record count")
            if not table_exists_flag or last_modified_date is None:
                # First-time sync with forced bulk API
                method = "bulk_api_full"
            else:
                # Incremental sync with forced bulk API
                method = "bulk_api_incremental"
        else:
            # Determine sync method based on record count thresholds
            if not table_exists_flag or last_modified_date is None:
                # First-time sync
                logger.debug("🆕 First-time sync detected")
                logger.debug(f"📊 Record count: {estimated_records}, Bulk API threshold: {self.BULK_API_THRESHOLD}")
                
                if estimated_records >= self.BULK_API_THRESHOLD:
                    method = "bulk_api_full"
                else:
                    method = "regular_api_full"
            else:            
                # For incremental syncs, prefer REST API unless there are very large changes
                if estimated_records >= 10000:  # Only use Bulk API for very large incremental changes
                    method = "bulk_api_incremental"
                    logger.debug(f"📊 Using bulk API incremental (large changes: {estimated_records} >= 100,000)")
                else:
                    method = "regular_api_incremental"
        
        strategy = {
            'method': method,
            'estimated_records': estimated_records,
            'is_incremental': table_exists_flag and last_modified_date is not None,
            'last_modified_date': last_modified_date
        }
        
        logger.debug(f"🎯 Final strategy: {strategy}")
        
        # Additional validation for first-time syncs
        if not table_exists_flag and strategy['method'].startswith('regular_api'):
            logger.warning(f"⚠️ Warning: First-time sync with large dataset using regular API. This may be inefficient.")
            logger.warning(f"⚠️ Consider using Bulk API for datasets with {estimated_records} records.")
        
        return strategy
    
    def _execute_sync_strategy(self, 
                             strategy: Dict[str, Any], 
                             sobject: str, 
                             schema: str, 
                             table: str,
                             match_field: str) -> Dict[str, Any]:
        """Execute the determined sync strategy."""
        
        method = strategy['method']
        logger.debug(f"🚀 Executing sync strategy: {method}")
        
        try:
            if method.startswith('bulk_api'):
                if self.existing_job_id:
                    logger.debug(f"🚀 Using existing job ID: {self.existing_job_id} - skipping query creation")
                    result = self._execute_bulk_api_with_existing_job(sobject, schema, table, strategy)
                else:
                    result = self._execute_bulk_api_sync(strategy, sobject, schema, table)
                return result
            elif method.startswith('regular_api'):
                logger.debug(f"📡 Using Regular API sync method: {method}")
                result = self._execute_regular_api_sync(strategy, sobject, schema, table, match_field)
                return result
            else:
                error_msg = f"Unknown sync method: {method}"
                logger.error(f"❌ {error_msg}")
                raise ValueError(error_msg)
                
        except Exception as e:
            error_msg = f"Error executing sync strategy: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                'success': False,
                'error': str(e),
                'records_processed': 0
            }
    
    def _execute_bulk_api_with_existing_job(self, 
                                          sobject: str, 
                                          schema: str, 
                                          table: str, 
                                          strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Bulk API sync using an existing job ID, skipping query creation."""
        
        logger.debug(f"🚀 Starting Bulk API sync with existing job ID: {self.existing_job_id}")
        
        # Get field descriptions for table creation (but don't create query)
        logger.debug(f"🔍 Getting field descriptions for {sobject}")
        try:
            from ..salesforce import sobjects
            query_string, df_fields, snowflake_fields = sobjects.describe(self.access_info, sobject, None)
            logger.debug(f"📋 Field descriptions: {df_fields}")
            logger.debug(f"📋 Snowflake field types: {snowflake_fields}")
            
            if not df_fields or not snowflake_fields:
                error_msg = f"Failed to get field descriptions for {sobject}"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
                    
        except Exception as e:
            error_msg = f"Error getting field descriptions for {sobject}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        # Skip query creation and go straight to job execution
        logger.debug(f"⏭️ Skipping query creation - using existing job ID: {self.existing_job_id}")
        return self._execute_bulk_api_job_with_id(sobject, schema, table, df_fields, snowflake_fields, strategy)
    
    def _execute_bulk_api_sync(self, 
                              strategy: Dict[str, Any], 
                              sobject: str, 
                              schema: str, 
                              table: str) -> Dict[str, Any]:
        """Execute Bulk API 2.0 sync with iterative field removal on errors."""
        
        logger.debug(f"🚀 Starting Bulk API sync for {sobject}")
        
        # Get the last modified date from the strategy (already queried)
        last_modified_date = strategy.get('last_modified_date')
        if last_modified_date:
            lmd_sf = str(last_modified_date)[:10] + 'T' + str(last_modified_date)[11:19] + '.000Z'
            logger.info(f"📅 Using LastModifiedDate for Salesforce query: {lmd_sf}")
        else:
            logger.info("📅 No LastModifiedDate - will sync all records from Salesforce")
        
        logger.debug(f"🔍 Getting field descriptions for {sobject}")
        try:
            from ..salesforce import sobjects
            query_string, df_fields, snowflake_fields = sobjects.describe(self.access_info, sobject, lmd_sf if last_modified_date else None)
            logger.info(f"📋 Salesforce Query: {query_string}")
            logger.debug(f"📋 Field descriptions: {df_fields}")
            logger.debug(f"📋 Snowflake field types: {snowflake_fields}")
            
            if not query_string or not df_fields:
                error_msg = f"Failed to get field descriptions for {sobject}"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
                    
        except Exception as e:
            error_msg = f"Error getting field descriptions for {sobject}: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        # Now execute the sync with iterative field removal
        return self._execute_bulk_api_with_retry(sobject, schema, table, df_fields, snowflake_fields, last_modified_date, strategy)
    
    def _execute_bulk_api_with_retry(self, sobject: str, schema: str, table: str, 
                                   df_fields: Dict[str, str], snowflake_fields: Dict[str, str], 
                                   last_modified_date: Optional[pd.Timestamp], 
                                   strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Bulk API sync with automatic field removal on errors."""
        
        current_fields = df_fields.copy()
        removed_fields = []
        
        while current_fields:
            try:
                logger.debug(f"🔄 Trying with {len(current_fields)} fields...")
                
                # Build query string with current fields
                query_string = f"SELECT {', '.join(current_fields.keys())} FROM {sobject}"
                if last_modified_date:
                    lmd_sf = str(last_modified_date)[:10] + 'T' + str(last_modified_date)[11:19] + '.000Z'
                    query_string += f" WHERE LastModifiedDate > {lmd_sf}"
                
                # Try to create the Bulk API job
                from ..salesforce import query_bapi20
                job_response = query_bapi20.create_batch_query(self.access_info, query_string)
                
                # Check if job_response indicates an error
                if isinstance(job_response, list) and len(job_response) > 0:
                    # This is an error response - extract field names from error message
                    error_info = job_response[0]
                    error_message = error_info.get('message', 'Unknown error')
                    error_code = error_info.get('errorCode', 'UNKNOWN_ERROR')
                    
                    logger.error(f"❌ Bulk API job creation failed:")
                    logger.error(f"  - Error Code: {error_code}")
                    logger.error(f"  - Error Message: {error_message}")
                    
                    # Extract field names from error message
                    problematic_fields = self._extract_problematic_fields(error_message)
                    if problematic_fields:
                        logger.debug(f"🔍 Identified problematic fields: {problematic_fields}")
                        
                        # Remove problematic fields and retry
                        for field in problematic_fields:
                            if field in current_fields:
                                del current_fields[field]
                                removed_fields.append(field)
                                logger.debug(f"🗑️ Removed field: {field}")
                        
                        if not current_fields:
                            raise Exception("No fields remaining after removing problematic fields")
                        
                        logger.debug(f"🔄 Retrying with {len(current_fields)} remaining fields...")
                        continue
                    else:
                        # If we can't identify specific fields, remove some fields and retry
                        logger.warning(f"⚠️ Could not identify specific problematic fields, removing some fields and retry...")
                        fields_to_remove = list(current_fields.keys())[-5:]  # Remove last 5 fields
                        for field in fields_to_remove:
                            if field in current_fields:
                                del current_fields[field]
                                removed_fields.append(field)
                                logger.debug(f"🗑️ Removed field: {field}")
                        
                        if not current_fields:
                            raise Exception("No fields remaining after removing fields")
                        
                        continue
                
                # If we get here, job creation was successful
                logger.info(f"✅ Successfully created Bulk API job with {len(current_fields)} fields")
                if removed_fields:
                    logger.info(f"🗑️ Removed {len(removed_fields)} problematic fields: {removed_fields}")
                
                # Now proceed with the actual sync using the working field set
                result = self._execute_bulk_api_job(sobject, schema, table, current_fields, snowflake_fields, last_modified_date, strategy)
                
                # If we get here, the job was successful
                return result
                
            except Exception as e:
                logger.warning(f"⚠️ Error during sync: {e}")
                # Remove some fields and retry
                fields_to_remove = list(current_fields.keys())[-3:]  # Remove last 3 fields
                for field in fields_to_remove:
                    if field in current_fields:
                        del current_fields[field]
                        removed_fields.append(field)
                        logger.debug(f"🗑️ Removed field: {field}")
                
                if not current_fields:
                    raise Exception("No fields remaining after removing fields")
                
                logger.debug(f"🔄 Retrying with {len(current_fields)} remaining fields...")
                continue
        
        # If we get here, we've exhausted all fields
        raise Exception("Failed to sync - no fields remaining")
    
    def _extract_problematic_fields(self, error_message: str) -> List[str]:
        """Extract field names from Salesforce error messages."""
        problematic_fields = []
        
        # Look for patterns like "No such column 'FieldName' on entity 'ObjectName'"
        import re
        
        # Pattern 1: "No such column 'FieldName' on entity"
        pattern1 = r"No such column '([^']+)' on entity"
        matches1 = re.findall(pattern1, error_message)
        problematic_fields.extend(matches1)
        
        # Pattern 2: "FieldName, FieldName2, FieldName3" (comma-separated list)
        # This often appears in the error message after the main error
        if '^' in error_message:
            # Extract the part after the ^ which often contains field names
            after_caret = error_message.split('^')[-1].strip()
            # Look for field names in this section
            field_pattern = r'\b[A-Za-z][A-Za-z0-9_]*\b'
            potential_fields = re.findall(field_pattern, after_caret)
            # Filter out common non-field words
            exclude_words = {'ERROR', 'Row', 'Column', 'entity', 'If', 'you', 'are', 'attempting', 'to', 'use', 'custom', 'field', 'be', 'sure', 'append', 'after', 'entity', 'name', 'Please', 'reference', 'WSDL', 'describe', 'call', 'appropriate', 'names'}
            for field in potential_fields:
                if field not in exclude_words and len(field) > 2:
                    problematic_fields.append(field)
        
        return list(set(problematic_fields))  # Remove duplicates
    
    def _execute_bulk_api_job_with_id(self, sobject: str, schema: str, table: str, 
                                     df_fields: Dict[str, str], snowflake_fields: Dict[str, str], 
                                     strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Bulk API sync using an existing job ID."""
        
        job_id = self.existing_job_id
        logger.debug(f"📋 Using existing Bulk API job: {job_id}")
        
        # Validate that the job ID exists and is accessible
        logger.debug("🔍 Validating existing job ID...")
        from ..salesforce import query_bapi20
        
        try:
            # Check if the job exists by querying its status
            status_response = query_bapi20.query_status(self.access_info, 'QueryAll', job_id)
            
            # Check if the response indicates the job doesn't exist
            if isinstance(status_response, list) and len(status_response) > 0:
                if 'errorCode' in status_response[0]:
                    error_code = status_response[0]['errorCode']
                    error_message = status_response[0].get('message', 'Unknown error')
                    
                    if 'NOT_FOUND' in error_code or 'NOT_FOUND' in error_message.upper():
                        error_msg = f"Job ID '{job_id}' not found. The job may have been deleted or never existed."
                        logger.error(f"❌ {error_msg}")
                        raise Exception(error_msg)
                    
                    # Check for other common error codes
                    if 'INVALID_ID' in error_code or 'INVALID_ID' in error_message.upper():
                        error_msg = f"Job ID '{job_id}' is invalid or malformed."
                        logger.error(f"❌ {error_msg}")
                        raise Exception(error_msg)
                    
                    # If there's any other error, raise it
                    error_msg = f"Error accessing job '{job_id}': {error_message} (Code: {error_code})"
                    logger.error(f"❌ {error_msg}")
                    raise Exception(error_msg)
            
            logger.info(f"✅ Job ID '{job_id}' validated successfully")
            
        except Exception as e:
            # Re-raise the exception if it's our custom error
            if "Job ID" in str(e):
                raise
            # Otherwise, provide a generic error message
            error_msg = f"Failed to validate job ID '{job_id}': {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise Exception(error_msg)
        
        # Monitor job status
        logger.debug("📊 Monitoring job status...")
        while True:
            status_response = query_bapi20.query_status(self.access_info, 'QueryAll', job_id)
            if isinstance(status_response, list) and len(status_response) > 0:
                job_status = status_response[0]
            else:
                job_status = status_response
            
            state = job_status['state']
            logger.debug(f"📊 Job status: {state}")
            
            if state == 'JobComplete':
                break
            elif state in ['Failed', 'Aborted']:
                error_msg = f"Bulk API job failed with state: {state}"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            time.sleep(10)
        
        # Get results
        
        logger.debug(f"📥 Getting results (optimized direct loading)")
        
        # Use optimized direct loading for all cases
        logger.debug(f"🔍 About to call get_bulk_results with force_full_sync={self.force_full_sync}")
        try:
            result = query_bapi20.get_bulk_results(
                self.session, self.access_info, job_id, sobject, schema, table,
                snowflake_fields=snowflake_fields,
                force_full_sync=self.force_full_sync
            )
            logger.info(f"✅ Bulk API results retrieved successfully")
        except Exception as e:
            logger.warning(f"⚠️ Warning: Error getting bulk results: {e}")
            result = None
        
        # Clean up job
        if self.delete_job:
            try:
                logger.debug(f"🧹 Cleaning up job: {job_id}")
                cleanup_result = query_bapi20.delete_specific_job(self.access_info, job_id)
                if cleanup_result.get('success'):
                    logger.info(f"🧹 Cleaned up job: {job_id}")
                else:
                    logger.warning(f"⚠️ Warning: Could not clean up job {job_id}: {cleanup_result.get('error', 'Unknown error')}")
            except Exception as e:
                logger.warning(f"⚠️ Warning: Could not clean up job {job_id}: {e}")
        else:
            logger.info(f"🧹 Skipping job cleanup (delete_job=False) - job {job_id} will remain in Salesforce")
        
        return {
            'success': True,
            'records_processed': strategy['estimated_records'],
            'job_id': job_id
        }
    
    def _execute_bulk_api_job(self, sobject: str, schema: str, table: str, 
                             df_fields: Dict[str, str], snowflake_fields: Dict[str, str], 
                             last_modified_date: Optional[pd.Timestamp], 
                             strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the actual Bulk API job after field filtering."""
        
        # Build the final query string with the working field set
        query_string = f"SELECT {', '.join(df_fields.keys())} FROM {sobject}"
        if last_modified_date:
            lmd_sf = str(last_modified_date)[:10] + 'T' + str(last_modified_date)[11:19] + '.000Z'
            query_string += f" WHERE LastModifiedDate > {lmd_sf}"
        
        logger.debug(f"🔍 Final SOQL query: {query_string}")
        logger.debug(f"🔍 Executing Bulk API query: {query_string}")
        
        # Create bulk query job
        logger.debug("📋 Creating Bulk API job...")
        from ..salesforce import query_bapi20
        job_response = query_bapi20.create_batch_query(self.access_info, query_string)
        
        # Check if job_response indicates an error
        if isinstance(job_response, list) and len(job_response) > 0:
            # This is an error response
            error_info = job_response[0]
            error_message = error_info.get('message', 'Unknown error')
            error_code = error_info.get('errorCode', 'UNKNOWN_ERROR')
            
            logger.error(f"❌ Bulk API job creation failed:")
            logger.error(f"  - Error Code: {error_code}")
            logger.error(f"  - Error Message: {error_message}")
            
            # Return error info instead of raising exception so retry logic can handle it
            return {
                'success': False,
                'error': f"Bulk API job creation failed: {error_code} - {error_message}",
                'error_code': error_code,
                'error_message': error_message,
                'records_processed': 0
            }
        
        # Check if job_response is a valid success response
        if not isinstance(job_response, dict) or 'id' not in job_response:
            logger.error(f"❌ Unexpected job_response format: {type(job_response)}")
            logger.error(f"❌ Expected dict with 'id' key, got: {job_response}")
            # Return error info instead of raising exception so retry logic can handle it
            return {
                'success': False,
                'error': f"Invalid job_response format: expected dict with 'id' key, got {type(job_response)}",
                'error_code': 'INVALID_FORMAT',
                'error_message': f"Invalid job_response format: expected dict with 'id' key, got {type(job_response)}",
                'records_processed': 0
            }
        
        job_id = job_response['id']
        
        logger.debug(f"📋 Created Bulk API job: {job_id}")
        logger.info(f"📋 Created Bulk API job: {job_id}")
        
        # Monitor job status
        logger.debug("📊 Monitoring job status...")
        while True:
            status_response = query_bapi20.query_status(self.access_info, 'QueryAll', job_id)
            if isinstance(status_response, list) and len(status_response) > 0:
                job_status = status_response[0]
            else:
                job_status = status_response
            
            state = job_status['state']
            logger.debug(f"📊 Job status: {state}")
            
            if state == 'JobComplete':
                break
            elif state in ['Failed', 'Aborted']:
                error_msg = f"Bulk API job failed with state: {state}"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            time.sleep(10)
        
        # Get results
        
        logger.debug(f"📥 Getting results (optimized direct loading)")
        
        # Use optimized direct loading for all cases
        logger.debug(f"🔍 About to call get_bulk_results with force_full_sync={self.force_full_sync}")
        try:
            result = query_bapi20.get_bulk_results(
                self.session, self.access_info, job_id, sobject, schema, table,
                snowflake_fields=snowflake_fields,
                force_full_sync=self.force_full_sync
            )
            logger.info(f"✅ Bulk API results retrieved successfully")
        except Exception as e:
            logger.warning(f"⚠️ Warning: Error getting bulk results: {e}")
            result = None
        
        # Clean up job
        if self.delete_job:
            try:
                logger.debug(f"🧹 Cleaning up job: {job_id}")
                cleanup_result = query_bapi20.delete_specific_job(self.access_info, job_id)
                if cleanup_result.get('success'):
                    logger.info(f"🧹 Cleaned up job: {job_id}")
                else:
                    logger.warning(f"⚠️ Warning: Could not clean up job {job_id}: {cleanup_result.get('error', 'Unknown error')}")
            except Exception as e:
                logger.warning(f"⚠️ Warning: Could not clean up job {job_id}: {e}")
        else:
            logger.info(f"🧹 Skipping job cleanup (delete_job=False) - job {job_id} will remain in Salesforce")
        
        return {
            'success': True,
            'records_processed': strategy['estimated_records'],
            'job_id': job_id
        }
    
    def _execute_regular_api_sync(self, 
                                 strategy: Dict[str, Any], 
                                 sobject: str, 
                                 schema: str, 
                                 table: str,
                                 match_field: str) -> Dict[str, Any]:
        """Execute regular API sync using sobject_query."""
        
        logger.debug(f"🚀 Starting regular API sync for {sobject}")
        
        # Get the last modified date from the strategy (already queried)
        last_modified_date = strategy.get('last_modified_date')
        if last_modified_date:
            lmd_sf = str(last_modified_date)[:10] + 'T' + str(last_modified_date)[11:19] + '.000Z'
            logger.info(f"📅 Using LastModifiedDate for Salesforce query: {lmd_sf}")
        else:
            logger.info("📅 No LastModifiedDate - will sync all records from Salesforce")
        
        logger.debug(f"🔍 Getting field descriptions for {sobject}")
        from ..salesforce import sobjects
        query_string, df_fields, snowflake_fields = sobjects.describe(self.access_info, sobject, lmd_sf if last_modified_date else None)
        logger.info(f"📋 Salesforce Query: {query_string}")
        
        # Convert query string to proper SOQL
        soql_query = query_string.replace('+', ' ').replace('select', 'SELECT').replace('from', 'FROM')
        if last_modified_date:
            soql_query = soql_query.replace('where', 'WHERE').replace('LastModifiedDate>', 'LastModifiedDate > ')
        
        logger.debug(f"🔍 Final SOQL query: {soql_query}")
        logger.debug(f"🔍 Executing regular API query: {soql_query}")
        
        # Execute query and process results
        records_processed = 0
        
        logger.info(f"🔄 Checking if incremental sync should be performed...")
        logger.info(f"   Strategy method: {strategy['method']}")
        logger.info(f"   Strategy is_incremental: {strategy['is_incremental']}")
        logger.info(f"   Table exists: {table_exists_flag}")
        logger.info(f"   Last modified date: {strategy.get('last_modified_date')}")
        
        if strategy['is_incremental']:
            logger.info("🔄 Performing INCREMENTAL sync with merge logic")
            # Incremental sync - use merge logic
            # First check if the main table exists before creating temp table
            if not table_exists(self.session, schema, table):
                error_msg = f"Cannot perform incremental sync: table {schema}.{table} does not exist"
                logger.error(f"❌ {error_msg}")
                raise Exception(error_msg)
            
            # Get current database for fully qualified table names
            current_db = self.session.sql('SELECT CURRENT_DATABASE()').collect()[0][0]
            from ..salesforce import sobject_sync
            
            logger.info("🔄 Calling sobject_sync.new_changed_records for incremental sync...")
            query_result = sobject_sync.new_changed_records(self.session, self.access_info, sobject, table, match_field)
            logger.info(f"🔄 Incremental sync completed. Query result: {query_result}")
            
            # For incremental sync, we need to estimate records processed
            # This is a limitation - sobject_sync doesn't return record count
            records_processed = estimated_records  # Use estimated count as approximation
            
        else:
            logger.info("🔄 Performing FULL sync (overwriting table)")
            # Full sync - overwrite table
            logger.debug("📥 Processing batches for full sync...")
            from ..salesforce import sobject_query
            for batch_num, batch_df in enumerate(sobject_query.query_records(self.access_info, soql_query), 1):
                if batch_df is not None and not batch_df.empty:
                    logger.debug(f"📦 Processing batch {batch_num}: {len(batch_df)} records")
                    # Let data_writer handle all formatting
                    import numpy as np
                    formatted_df = batch_df.replace(np.nan, None)
                    
                    # Write to table using centralized data writer with type handling
                    is_first_batch = records_processed == 0
                    logger.debug(f"💾 Writing batch {batch_num} to table {schema}.{table} (overwrite={is_first_batch})")
                    
                    # Use type handling to prevent casting errors
                    try:
                        from ..util import data_writer
                        data_writer.write_batch_to_main_table(
                            self.session, formatted_df, schema, table, is_first_batch,
                            validate_types=True,
                            use_logical_type=False,  # More lenient for problematic data
                            df_fields=df_fields,  # Pass field definitions for proper formatting
                            snowflake_fields=snowflake_fields,  # Pass Salesforce field types for proper table creation
                            force_full_sync=self.force_full_sync  # Pass force_full_sync parameter
                        )
                    except Exception as e:
                        error_msg = str(e)
                        if any(phrase in error_msg for phrase in ["Failed to cast", "cast", "variant", "FIXED"]):
                            logger.warning(f"⚠️ Casting error detected: {error_msg[:100]}...")
                            logger.warning(f"⚠️ Retrying with type standardization...")
                            # Standardize types and retry
                            df_standardized = data_writer.standardize_dataframe_types(formatted_df, "string")
                            data_writer.write_batch_to_main_table(
                                self.session, df_standardized, schema, table, is_first_batch,
                                validate_types=False,
                                use_logical_type=False,
                                df_fields=df_fields,  # Pass field definitions for proper formatting
                                snowflake_fields=snowflake_fields,  # Pass Salesforce field types for proper table creation
                                force_full_sync=self.force_full_sync  # Pass force_full_sync parameter
                            )
                        else:
                            logger.error(f"❌ Non-casting error: {error_msg}")
                            raise
                    
                    records_processed += len(batch_df)
        
        logger.debug(f"✅ Regular API sync completed: {records_processed} records processed")
        return {
            'success': True,
            'records_processed': records_processed
        }
    
    def _create_error_result(self, sobject: str, schema: str, table: str, error_msg: str) -> Dict[str, Any]:
        """Create a standardized error result."""
        return {
            'sobject': sobject,
            'target_table': f"{schema}.{table}",
            'sync_method': 'failed',
            'estimated_records': 0,
            'actual_records': 0,
            'sync_duration_seconds': 0,
            'last_modified_date': None,
            'sync_timestamp': pd.Timestamp.now(),
            'success': False,
            'error': error_msg
        }


def sync_sobject_intelligent(session: Session, 
                           access_info: Dict[str, str],
                           sobject: str, 
                           schema: str, 
                           table: str, 
                           match_field: str = 'ID',
                           force_full_sync: bool = False,
                           force_bulk_api: bool = False,
                           existing_job_id: Optional[str] = None,
                           delete_job: bool = True) -> Dict[str, Any]:
    """
    Convenience function for intelligent SObject synchronization.
    
    Args:
        session: Snowflake Snowpark session
        access_info: Dictionary containing Salesforce access details
        sobject: Salesforce SObject name (e.g., 'Account', 'Contact')
        schema: Snowflake schema name
        table: Snowflake table name
        match_field: Field to use for matching records (default: 'ID')
        force_full_sync: Force a full sync regardless of previous sync status
        force_bulk_api: Force use of Bulk API 2.0 instead of regular API
        existing_job_id: Optional existing Bulk API job ID to use
        delete_job: Whether to delete the Bulk API job after completion
        
    Returns:
        Dictionary containing sync results and metadata
    """
    sync_system = IntelliSync(session, access_info)
    return sync_system.sync_sobject(
        sobject, schema, table, match_field, 
        force_full_sync, force_bulk_api, existing_job_id, delete_job
    )
