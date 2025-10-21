import requests
import json
import csv as csv_module
import io
import logging
from snowflake.snowpark import Session
from snowflake.snowpark.exceptions import SnowparkSQLException

logger = logging.getLogger(__name__)

def create_logs_schema_if_not_exists(session: Session):
    """Create the logs schema if it doesn't exist."""
    try:
        session.sql("CREATE SCHEMA IF NOT EXISTS LOGS").collect()
        logger.info("✅ LOGS schema created/verified successfully")
    except Exception as e:
        logger.warning(f"⚠️ Warning: Could not create LOGS schema: {e}")

def create_job_info_table(session: Session):
    """Create the job_info table based on Salesforce API documentation."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS LOGS.JOB_INFO (
        ID VARCHAR(255) PRIMARY KEY,
        OPERATION VARCHAR(50),
        OBJECT VARCHAR(255),
        CREATED_BY_ID VARCHAR(255),
        CREATED_DATE TIMESTAMP_NTZ,
        SYSTEM_MODSTAMP TIMESTAMP_NTZ,
        STATE VARCHAR(20),
        JOB_TYPE VARCHAR(50),
        NUMBER_RECORDS_PROCESSED INTEGER,
        NUMBER_RECORDS_FAILED INTEGER,
        RETRY_COUNT INTEGER,
        TOTAL_PROCESSING_TIME INTEGER,
        API_ACTIVE_PROCESSING_TIME INTEGER,
        AVERAGE_PER_SECOND INTEGER,
        AVERAGE_PER_BATCH INTEGER,
        NUMBER_RECORDS_TOTAL INTEGER,
        NUMBER_BATCHES_TOTAL INTEGER,
        NUMBER_BATCHES_IN_PROGRESS INTEGER,
        NUMBER_BATCHES_COMPLETED INTEGER,
        NUMBER_BATCHES_FAILED INTEGER,
        NUMBER_BATCHES_PENDING INTEGER,
        BYTES_PROCESSED INTEGER,
        ERROR_CODE VARCHAR(255),
        ERROR_MESSAGE VARCHAR(16777216),
        CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
    )
    """
    try:
        session.sql(create_table_sql).collect()
        logger.info("✅ JOB_INFO table created/verified successfully")
    except Exception as e:
        logger.warning(f"⚠️ Warning: Could not create JOB_INFO table: {e}")

def create_success_table(session: Session):
    """Create the success table based on Salesforce API documentation."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS LOGS.SUCCESS (
        ID INTEGER IDENTITY PRIMARY KEY,
        JOB_ID VARCHAR(255) NOT NULL,
        SF_ID VARCHAR(255),
        CREATED TIMESTAMP_NTZ,
        SUCCESS BOOLEAN,
        ERRORS VARCHAR(16777216),
        CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
    )
    """
    try:
        session.sql(create_table_sql).collect()
        logger.info("✅ SUCCESS table created/verified successfully")
    except Exception as e:
        logger.warning(f"⚠️ Warning: Could not create SUCCESS table: {e}")

def create_failure_table(session: Session):
    """Create the failure table based on Salesforce API documentation."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS LOGS.FAILURE (
        ID INTEGER IDENTITY PRIMARY KEY,
        JOB_ID VARCHAR(255) NOT NULL,
        SF_ID VARCHAR(255),
        SF_ERROR VARCHAR(16777216),
        CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
    )
    """
    try:
        session.sql(create_table_sql).collect()
        logger.info("✅ FAILURE table created/verified successfully")
    except Exception as e:
        logger.warning(f"⚠️ Warning: Could not create FAILURE table: {e}")

def get_job_info(access_info: dict, job_id: str) -> dict:
    """Retrieve job information from Salesforce Bulk API 2.0."""
    access_token = access_info['access_token']
    url = f"{access_info['instance_url']}/services/data/v62.0/jobs/ingest/{job_id}"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_info = {
            'error': True,
            'error_code': getattr(e.response, 'status_code', 'UNKNOWN') if hasattr(e, 'response') else 'UNKNOWN',
            'error_message': str(e),
            'state': 'Failed'
        }
        logger.error(f"❌ Error retrieving job info: {error_info}")
        return error_info

def get_successful_results(access_info: dict, job_id: str) -> list:
    """Retrieve successful results from Salesforce Bulk API 2.0."""
    access_token = access_info['access_token']
    url = f"{access_info['instance_url']}/services/data/v62.0/jobs/ingest/{job_id}/successfulResults/"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'text/csv'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse CSV response
        csv_content = response.text
        if not csv_content.strip():
            logger.info("ℹ️ No CSV content received for successful results")
            return []
            
        # Parse CSV and convert to list of dictionaries
        try:
            csv_reader = csv_module.DictReader(io.StringIO(csv_content))
            results = []
            for row in csv_reader:
                results.append(row)
            
            logger.info(f"✅ Successfully parsed {len(results)} successful records from CSV")
            return results
            
        except Exception as csv_error:
            logger.warning(f"⚠️ Warning: CSV parsing error for successful results: {csv_error}")
            logger.debug(f"📄 CSV content preview: {csv_content[:200]}...")
            return []
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error retrieving successful results: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Error parsing successful results CSV: {e}")
        return []

def get_failed_results(access_info: dict, job_id: str) -> list:
    """Retrieve failed results from Salesforce Bulk API 2.0."""
    access_token = access_info['access_token']
    url = f"{access_info['instance_url']}/services/data/v62.0/jobs/ingest/{job_id}/failedResults/"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'text/csv'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse CSV response
        csv_content = response.text
        if not csv_content.strip():
            logger.info("ℹ️ No CSV content received for failed results")
            return []
            
        # Parse CSV and convert to list of dictionaries
        try:
            csv_reader = csv_module.DictReader(io.StringIO(csv_content))
            results = []
            for row in csv_reader:
                results.append(row)
            
            logger.info(f"✅ Successfully parsed {len(results)} failed records from CSV")
            
            # 🔍 DEBUG: Show sample of failed results structure
            if results:
			logger.debug(f"📋 Sample failed result structure:")
                logger.debug(f"   Keys: {list(results[0].keys())}")
                logger.debug(f"   Sample record: {results[0]}")
                logger.debug(f"   Total records: {len(results)}")
            
            return results
            
        except Exception as csv_error:
            logger.warning(f"⚠️ Warning: CSV parsing error for failed results: {csv_error}")
            logger.debug(f"📄 CSV content preview: {csv_content[:200]}...")
            return []
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error retrieving failed results: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Error parsing failed results CSV: {e}")
        return []

def insert_job_info(session: Session, job_data: dict, job_id: str):
    """Insert job information into the JOB_INFO table."""
    try:
        # Handle error cases
        if job_data.get('error'):
            insert_sql = f"""
            INSERT INTO LOGS.JOB_INFO (
                ID, OPERATION, OBJECT, CREATED_BY_ID, CREATED_DATE, SYSTEM_MODSTAMP,
                STATE, JOB_TYPE, NUMBER_RECORDS_PROCESSED, NUMBER_RECORDS_FAILED,
                RETRY_COUNT, TOTAL_PROCESSING_TIME, API_ACTIVE_PROCESSING_TIME,
                AVERAGE_PER_SECOND, AVERAGE_PER_BATCH, NUMBER_RECORDS_TOTAL,
                NUMBER_BATCHES_TOTAL, NUMBER_BATCHES_IN_PROGRESS, NUMBER_BATCHES_COMPLETED,
                NUMBER_BATCHES_FAILED, NUMBER_BATCHES_PENDING, BYTES_PROCESSED,
                ERROR_CODE, ERROR_MESSAGE
            ) VALUES (
                '{job_id}',
                NULL, NULL, NULL, NULL, NULL,
                '{job_data.get('state', 'Failed')}',
                NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                NULL, NULL, NULL, NULL, NULL, NULL,
                '{str(job_data.get('error_code', '')).replace(chr(39), chr(39)+chr(39))}',
                '{str(job_data.get('error_message', '')).replace(chr(39), chr(39)+chr(39))}'
            )
            """
        else:
            # Normal job data - safely escape string values and handle NULLs properly
            operation = f"'{str(job_data.get('operation', '')).replace(chr(39), chr(39)+chr(39))}'" if job_data.get('operation') else 'NULL'
            object_name = f"'{str(job_data.get('object', '')).replace(chr(39), chr(39)+chr(39))}'" if job_data.get('object') else 'NULL'
            created_by_id = f"'{str(job_data.get('createdById', '')).replace(chr(39), chr(39)+chr(39))}'" if job_data.get('createdById') else 'NULL'
            # Format timestamps: replace 'T' with space and remove '+0000'
            created_date_raw = job_data.get('createdDate')
            created_date = f"TO_TIMESTAMP_NTZ(TO_TIMESTAMP_TZ('{created_date_raw.replace('T', ' ').replace('+0000', '')}'))" if created_date_raw else 'NULL'
            
            system_modstamp_raw = job_data.get('systemModstamp')
            system_modstamp = f"TO_TIMESTAMP_NTZ(TO_TIMESTAMP_TZ('{system_modstamp_raw.replace('T', ' ').replace('+0000', '')}'))" if system_modstamp_raw else 'NULL'
            state = f"'{str(job_data.get('state', '')).replace(chr(39), chr(39)+chr(39))}'" if job_data.get('state') else 'NULL'
            job_type = f"'{str(job_data.get('jobType', '')).replace(chr(39), chr(39)+chr(39))}'" if job_data.get('jobType') else 'NULL'
            
            # Handle error fields properly
            error_code = f"'{str(job_data.get('errorCode', '')).replace(chr(39), chr(39)+chr(39))}'" if job_data.get('errorCode') else 'NULL'
            error_message = f"'{str(job_data.get('errorMessage', '')).replace(chr(39), chr(39)+chr(39))}'" if job_data.get('errorMessage') else 'NULL'
            
            insert_sql = f"""
            INSERT INTO LOGS.JOB_INFO (
                ID, OPERATION, OBJECT, CREATED_BY_ID, CREATED_DATE, SYSTEM_MODSTAMP,
                STATE, JOB_TYPE, NUMBER_RECORDS_PROCESSED, NUMBER_RECORDS_FAILED,
                RETRY_COUNT, TOTAL_PROCESSING_TIME, API_ACTIVE_PROCESSING_TIME,
                AVERAGE_PER_SECOND, AVERAGE_PER_BATCH, NUMBER_RECORDS_TOTAL,
                NUMBER_BATCHES_TOTAL, NUMBER_BATCHES_IN_PROGRESS, NUMBER_BATCHES_COMPLETED,
                NUMBER_BATCHES_FAILED, NUMBER_BATCHES_PENDING, BYTES_PROCESSED,
                ERROR_CODE, ERROR_MESSAGE
            ) VALUES (
                '{job_id}',
                {operation},
                {object_name},
                {created_by_id},
                {created_date},
                {system_modstamp},
                {state},
                {job_type},
                {job_data.get('numberRecordsProcessed') or 'NULL'},
                {job_data.get('numberRecordsFailed') or 'NULL'},
                {job_data.get('retryCount') or 'NULL'},
                {job_data.get('totalProcessingTime') or 'NULL'},
                {job_data.get('apiActiveProcessingTime') or 'NULL'},
                {job_data.get('averagePerSecond') or 'NULL'},
                {job_data.get('averagePerBatch') or 'NULL'},
                {job_data.get('numberRecordsTotal') or 'NULL'},
                {job_data.get('numberBatchesTotal') or 'NULL'},
                {job_data.get('numberBatchesInProgress') or 'NULL'},
                {job_data.get('numberBatchesCompleted') or 'NULL'},
                {job_data.get('numberBatchesFailed') or 'NULL'},
                {job_data.get('numberBatchesPending') or 'NULL'},
                {job_data.get('bytesProcessed') or 'NULL'},
                {error_code},
                {error_message}
            )
            """

        
        session.sql(insert_sql).collect()
        logger.info(f"✅ Job info inserted for job {job_id}")
        
    except Exception as e:
        logger.error(f"❌ Error inserting job info: {e}")
        		logger.error(f"📋 SQL that failed: {insert_sql}")

def insert_success_records(session: Session, job_id: str, success_data: list):
    """Insert successful records into the SUCCESS table."""
    if not success_data:
        logger.info("ℹ️ No successful records to insert")
        return
    
    try:
        for record in success_data:
            # Safely escape string values and handle NULLs properly
            sf_id = f"'{str(record.get('sf__Id', '')).replace(chr(39), chr(39)+chr(39))}'" if record.get('sf__Id') else 'NULL'
            
            # Format timestamps: replace 'T' with space and remove '+0000'
            created_raw = record.get('sf__Created')
            created = f"TO_TIMESTAMP_NTZ(TO_TIMESTAMP_TZ('{str(created_raw).replace('T', ' ').replace('+0000', '').replace(chr(39), chr(39)+chr(39))}'))" if created_raw else 'NULL'
            
            success = f"'{str(record.get('sf__Success', '')).replace(chr(39), chr(39)+chr(39))}'" if record.get('sf__Success') else 'NULL'
            errors = f"'{json.dumps(record.get('sf__Errors')).replace(chr(39), chr(39)+chr(39))}'" if record.get('sf__Errors') else 'NULL'
            
            insert_sql = f"""
            INSERT INTO LOGS.SUCCESS (
                JOB_ID, SF_ID, CREATED, SUCCESS, ERRORS
            ) VALUES (
                '{job_id}',
                {sf_id},
                {created},
                {success},
                {errors}
            )
            """
            
            session.sql(insert_sql).collect()
        
        logger.info(f"✅ Inserted {len(success_data)} successful records for job {job_id}")
        
    except Exception as e:
        logger.error(f"❌ Error inserting success records: {e}")

def insert_failure_records(session: Session, job_id: str, failure_data: list):
    """Insert failed records into the FAILURE table."""
    if not failure_data:
        logger.info("ℹ️ No failed records to insert")
        return
    
    		logger.info(f"📋 Starting to insert {len(failure_data)} failed records for job {job_id}")
    
    try:
        for i, record in enumerate(failure_data):
			logger.debug(f"📋 Processing failed record {i+1}/{len(failure_data)}")
            logger.debug(f"   Raw record: {record}")
            logger.debug(f"   Record keys: {list(record.keys())}")
            
            # Safely escape string values and handle NULLs properly
            sf_id = f"'{str(record.get('sf__Id', '')).replace(chr(39), chr(39)+chr(39))}'" if record.get('sf__Id') else 'NULL'
            
            # Get error information
            sf_error = f"'{str(record.get('sf__Error', '')).replace(chr(39), chr(39)+chr(39))}'" if record.get('sf__Error') else 'NULL'
            
            logger.debug(f"   Processed values:")
            logger.debug(f"     sf_id: {sf_id}")
            logger.debug(f"     sf_error: {sf_error}")
            
            insert_sql = f"""
            INSERT INTO LOGS.FAILURE (
                JOB_ID, SF_ID, SF_ERROR
            ) VALUES (
                '{job_id}',
                {sf_id},
                {sf_error}
            )
            """
            
            logger.debug(f"   Generated SQL: {insert_sql}")
            
            try:
                result = session.sql(insert_sql).collect()
                logger.debug(f"   ✅ SQL execution successful: {result}")
            except Exception as sql_error:
                logger.error(f"   ❌ SQL execution failed: {sql_error}")
                logger.error(f"   SQL that failed: {insert_sql}")
                raise sql_error
        
        logger.info(f"✅ Inserted {len(failure_data)} failed records for job {job_id}")
        
    except Exception as e:
        logger.error(f"❌ Error inserting failure records: {e}")
        		logger.error(f"📋 Last processed record index: {i if 'i' in locals() else 'N/A'}")
        raise

def process_bulk_api_results(session: Session, access_info: dict, job_id: str):
    """
    Main function to process Bulk API 2.0 job results and store them in the database.
    
    Args:
        session: Snowflake session object
        access_info: Salesforce access credentials dictionary
        job_id: The Bulk API 2.0 job ID to process
    """
    logger.info(f"🚀 Processing Bulk API 2.0 results for job: {job_id}")
    
    try:
        # Step 1: Create schema and tables if they don't exist
        logger.info("📋 Setting up database schema and tables...")
        create_logs_schema_if_not_exists(session)
        create_job_info_table(session)
        create_success_table(session)
        create_failure_table(session)
        
        # Step 2: Retrieve job information
        logger.info(f"📊 Retrieving job information for job {job_id}...")
        job_info = get_job_info(access_info, job_id)
        
        # Step 3: Insert job information
        logger.info("💾 Storing job information...")
        insert_job_info(session, job_info, job_id)
        
        # Step 4: Retrieve and store successful results
        logger.info("📈 Retrieving successful results...")
        success_results = get_successful_results(access_info, job_id)
        insert_success_records(session, job_id, success_results)
        
        # Step 5: Retrieve and store failed results
        logger.info("📉 Retrieving failed results...")
        failure_results = get_failed_results(access_info, job_id)
        
        		logger.debug(f"📋 Failure results summary:")
        logger.debug(f"   Type: {type(failure_results)}")
        logger.debug(f"   Length: {len(failure_results) if failure_results else 0}")
        logger.debug(f"   Is empty: {not failure_results}")
        
        if failure_results:
            logger.debug(f"   First record keys: {list(failure_results[0].keys())}")
            logger.debug(f"   Sample first record: {failure_results[0]}")
        
        insert_failure_records(session, job_id, failure_results)
        
        # Step 6: Summary
        logger.info("✅ BULK API 2.0 RESULTS PROCESSING COMPLETED")
        logger.info(f"📊 Job ID: {job_id}")
        logger.info(f"📈 Successful Records: {len(success_results)}")
        logger.info(f"📉 Failed Records: {len(failure_results)}")
        logger.info(f"🗄️ Data stored in LOGS schema tables")
        
        return {
            'job_id': job_id,
            'success_count': len(success_results),
            'failure_count': len(failure_results),
            'job_state': job_info.get('state', 'Unknown'),
            'success': True
        }
        
    except Exception as e:
        logger.error(f"❌ ERROR processing Bulk API 2.0 results: {e}")
        return {
            'job_id': job_id,
            'success_count': 0,
            'failure_count': 0,
            'job_state': 'Error',
            'success': False,
            'error': str(e)
        }

# Legacy function for backward compatibility
def successful_results(access_info, job_id):
    """Legacy function - now redirects to the new comprehensive processing."""
    logger.warning("⚠️ Warning: This function is deprecated. Use process_bulk_api_results() instead.")
    return get_successful_results(access_info, job_id)