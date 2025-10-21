"""
Synchronization utility functions for Salesforce to Snowflake sync operations.
This module provides core utility functions for determining sync status and requirements.
"""

import pandas as pd
import requests
import logging
from typing import Optional, Dict, Any
from snowflake.snowpark import Session

logger = logging.getLogger(__name__)


def sql_execution(session: Session, query: str, context: str = "") -> list:
    """SQL execution with error handling."""
    try:
        return session.sql(query).collect()
    except Exception as e:
        logger.error(f"SQL Error in {context}: {e}")
        raise


def table_exists(session: Session, schema: str, table: str) -> bool:
    """
    Check if the target table exists in Snowflake.
    
    Args:
        session: Snowflake Snowpark session
        schema: Schema name
        table: Table name
        
    Returns:
        bool: True if table exists, False otherwise
    """
    try:
        # First check if schema exists
        schema_query = f"SHOW SCHEMAS LIKE '{schema}'"
        schema_result = sql_execution(session, schema_query, "schema_check")
        
        if not schema_result or len(schema_result) == 0:
            logger.debug(f"📋 Schema {schema} does not exist")
            return False
        
        # Then check if table exists in schema
        current_db = session.sql('SELECT CURRENT_DATABASE()').collect()[0][0]
        query = f"SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = '{schema}' AND table_name = '{table}' AND table_type = 'BASE TABLE'"
        result = sql_execution(session, query, "table_check")
        
        # More robust result checking
        if result is not None and len(result) > 0:
            # Check if result has the expected structure
            if 'table_count' in result[0]:
                exists = result[0]['table_count'] > 0
            else:
                # Fallback: check if any result was returned
                exists = len(result) > 0
        else:
            exists = False
            
        logger.debug(f"📋 Table {schema}.{table} exists: {exists}")
        return exists
    except Exception as e:
        logger.error(f"❌ Error checking table existence: {e}")
        return False


def get_last_modified_date(session: Session, schema: str, table: str) -> Optional[pd.Timestamp]:
    """
    Get the most recent LastModifiedDate from the target table.
    
    Args:
        session: Snowflake Snowpark session
        schema: Schema name
        table: Table name
        
    Returns:
        Optional[pd.Timestamp]: Most recent LastModifiedDate or None if not found
    """
    try:
        # Check that table exists before querying
        if not table_exists(session, schema, table):
            logger.debug(f"📋 Table {schema}.{table} does not exist, skipping last modified date check")
            return None
        
        # Get current database for fully qualified table name
        current_db = session.sql('SELECT CURRENT_DATABASE()').collect()[0][0]
        
        # First check if LASTMODIFIEDDATE column exists
        try:
            desc_query = f"DESCRIBE TABLE {current_db}.{schema}.{table}"
            desc_result = sql_execution(session, desc_query, "describe_table")
            logger.info(f"🔍 Table structure: {desc_result}")
            
            # Check if LASTMODIFIEDDATE column exists
            has_last_modified = any('LASTMODIFIEDDATE' in str(row).upper() for row in desc_result)
            logger.info(f"🔍 Has LASTMODIFIEDDATE column: {has_last_modified}")
            
            if not has_last_modified:
                logger.info("📅 LASTMODIFIEDDATE column not found in table - cannot perform incremental sync")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Could not describe table structure: {e}")
        
        # Try to get the last modified date
        try:
            query = f"SELECT MAX(LASTMODIFIEDDATE) as LAST_MODIFIED FROM {current_db}.{schema}.{table}"
            logger.info(f"🔍 Executing LastModifiedDate query: {query}")
            result = sql_execution(session, query, "last_modified_date")
            
            logger.info(f"🔍 Query result: {result}")
            logger.info(f"🔍 Result type: {type(result)}")
            logger.info(f"🔍 Result length: {len(result) if result else 0}")
            
            if result and len(result) > 0:
                # Handle Snowflake Row objects properly
                row = result[0]
                logger.info(f"🔍 Row: {row}")
                logger.info(f"🔍 Row type: {type(row)}")
                logger.info(f"🔍 Row attributes: {dir(row)}")
                
                if hasattr(row, 'LAST_MODIFIED') and row.LAST_MODIFIED:
                    last_modified = pd.to_datetime(row.LAST_MODIFIED)
                    logger.info(f"📅 Last modified date found: {last_modified}")
                    return last_modified
                elif hasattr(row, '__getitem__'):
                    # Fallback to dictionary-style access
                    try:
                        last_modified_value = row['LAST_MODIFIED']
                        logger.info(f"🔍 Last modified value: {last_modified_value}")
                        if last_modified_value:
                            last_modified = pd.to_datetime(last_modified_value)
                            logger.info(f"📅 Last modified date found: {last_modified}")
                            return last_modified
                        else:
                            logger.info("📅 Last modified value is None/empty")
                    except (KeyError, TypeError) as e:
                        logger.info(f"🔍 Dictionary access failed: {e}")
                        pass
                        
        except Exception as e:
            logger.warning(f"⚠️ First attempt failed, trying alternative approach: {e}")
            
            try:
                # Alternative: try to get the last modified date without casting
                query = f"SELECT MAX(LASTMODIFIEDDATE) as LAST_MODIFIED FROM {current_db}.{schema}.{table}"
                result = sql_execution(session, query, "last_modified_date_alt")
                
                if result and len(result) > 0:
                    row = result[0]
                    raw_value = None
                    
                    if hasattr(row, 'LAST_MODIFIED') and row.LAST_MODIFIED:
                        raw_value = row.LAST_MODIFIED
                    elif hasattr(row, '__getitem__'):
                        try:
                            raw_value = row['LAST_MODIFIED']
                        except (KeyError, TypeError):
                            pass
                    
                    if isinstance(raw_value, str):
                        # Handle Salesforce ISO 8601 format: 2023-09-08T02:00:39.000Z
                        try:
                            last_modified = pd.to_datetime(raw_value, errors='coerce')
                            if pd.notna(last_modified):
                                logger.debug(f"📅 Converted last modified date: {last_modified}")
                                return last_modified
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to parse timestamp {raw_value}: {e}")
                    else:
                        # Handle numeric dates (Unix timestamps)
                        try:
                            last_modified = pd.to_datetime(raw_value, unit='ms', errors='coerce')
                            if pd.notna(last_modified):
                                logger.debug(f"📅 Converted last modified date: {last_modified}")
                                return last_modified
                        except:
                            # Fallback to seconds
                            last_modified = pd.to_datetime(raw_value, unit='s', errors='coerce')
                            if pd.notna(last_modified):
                                logger.debug(f"📅 Converted last modified date: {last_modified}")
                                return last_modified
                                
            except Exception as e2:
                logger.warning(f"⚠️ Alternative approach also failed: {e2}")
        
        logger.info("📅 No valid last modified date found - table may be empty or LASTMODIFIEDDATE column doesn't exist")
        return None
    except Exception as e:
        logger.error(f"❌ Error getting last modified date: {e}")
        return None


def ensure_schema_exists(session: Session, schema: str) -> bool:
    """
    Ensure the schema exists in Snowflake, create it if it doesn't.
    
    Args:
        session: Snowflake Snowpark session
        schema: Schema name
        
    Returns:
        bool: True if schema exists or was created successfully, False otherwise
    """
    try:
        schema_query = f"SHOW SCHEMAS LIKE '{schema}'"
        logger.debug(f"🔍 Checking if schema exists: {schema_query}")
        schema_result = sql_execution(session, schema_query, "schema_exists_check")
        
        if not schema_result or len(schema_result) == 0:
            logger.debug(f"📋 Schema {schema} does not exist, creating it...")
            create_schema_query = f"CREATE SCHEMA IF NOT EXISTS {schema}"
            logger.debug(f"🔍 Creating schema: {create_schema_query}")
            sql_execution(session, create_schema_query, "create_schema")
            logger.debug(f"✅ Schema {schema} created successfully")
            return True
        else:
            logger.debug(f"📋 Schema {schema} already exists")
            return True
    except Exception as e:
        logger.error(f"❌ Error ensuring schema exists: {e}")
        return False


def get_record_count(access_info: Dict[str, str], sobject: str, last_modified_date: Optional[pd.Timestamp] = None) -> int:
    """
    Get the count of records from Salesforce SObject.
    
    Args:
        access_info: Dictionary containing Salesforce access details
        sobject: Salesforce SObject name
        last_modified_date: Optional timestamp for incremental sync. If provided, only counts records
                          modified after this date. If None, counts all records.
        
    Returns:
        int: Number of records matching the criteria
    """
    try:
        # Build query to count records
        if last_modified_date is not None:
            # Incremental sync - count records modified since last sync
            lmd_sf = str(last_modified_date)[:10] + 'T' + str(last_modified_date)[11:19] + '.000Z'
            query = f"SELECT COUNT(Id) FROM {sobject} WHERE LastModifiedDate > {lmd_sf}"
            logger.debug(f"🔍 Executing incremental record count query: {query}")
        else:
            # Full sync - count all records
            query = f"SELECT COUNT(Id) FROM {sobject}"
            logger.debug(f"🔍 Executing full record count query: {query}")
        
        # Use regular API for count (faster than Bulk API for counts)
        headers = {
            "Authorization": f"Bearer {access_info['access_token']}",
            "Content-Type": "application/json"
        }
        url = f"{access_info['instance_url']}/services/data/v58.0/query?q={query}"
        
        logger.debug(f"🌐 Making API request to: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        # Handle different response structures for COUNT queries
        if isinstance(result, dict):
            # For COUNT queries, check records array first
            if 'records' in result and len(result['records']) > 0:
                first_record = result['records'][0]
                
                # Try different possible field names for count
                count_fields = ['expr0', 'count', 'COUNT', 'count__c', 'Id']
                for field in count_fields:
                    if field in first_record:
                        count = first_record[field]
                        logger.debug(f"📊 Record count from {field}: {count}")
                        return count
                
                # If no expected field found, log the structure
                logger.warning(f"📊 Unexpected record structure: {first_record}")
            
            # Fallback to totalSize (though this should not be used for COUNT queries)
            if 'totalSize' in result:
                if 'records' in result and len(result['records']) > 0:
                    try:
                        if result['records'][0]['expr0'] > 0:
                            count = result['records'][0]['expr0']
                            return count
                    except (KeyError, IndexError, TypeError) as e:
                        logger.warning(f"⚠️ Warning: Could not determine record count: {e}")
        else:
            logger.warning(f"📊 Unexpected response type: {type(result)}")
            logger.warning("📊 No count found in response, using conservative estimate")
        
        return 1000 if last_modified_date is not None else 100000
        
    except Exception as e:
        logger.error(f"❌ Error getting record count: {e}")
        
        # Try to get more information about the response if available
        try:
            if 'response' in locals():
                logger.debug(f"📊 Response status: {response.status_code}")
                logger.debug(f"📊 Response headers: {dict(response.headers)}")
                logger.debug(f"📊 Response content: {response.text[:500]}...")
        except:
            pass
        
        # Return a conservative estimate
        estimate = 1000 if last_modified_date is not None else 100000
        logger.debug(f"📊 Using conservative estimate: {estimate}")
        return estimate
