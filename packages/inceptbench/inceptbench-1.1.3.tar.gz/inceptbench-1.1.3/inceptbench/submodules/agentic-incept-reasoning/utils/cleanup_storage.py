#!/usr/bin/env python3
import os
import logging
import argparse
import time
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any
from dotenv import load_dotenv, find_dotenv

from supabase import create_client, Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Suppress httpx HTTP request logs to reduce clutter
logging.getLogger("httpx").setLevel(logging.WARNING)

def get_supabase_client() -> Client:
    """Initialize and return Supabase client."""
    load_dotenv(find_dotenv())
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY environment variables must be set.")
    
    return create_client(supabase_url, supabase_key)

def list_bucket_files(
    client: Client, 
    bucket_name: str = "incept-images", 
    limit: int = 50,  # Reduced batch size for more reliable processing
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    List files in the specified storage bucket, sorted by creation date.
    Uses server-side sorting and pagination.
    
    Parameters
    ----------
    client : Client
        Initialized Supabase client
    bucket_name : str
        Name of the storage bucket
    limit : int
        Maximum number of files to return (default 50)
    offset : int
        Number of files to skip (for pagination)
    
    Returns
    -------
    List[Dict[str, Any]]
        List of file objects containing metadata including creation time
    """
    try:
        # Use the storage API's sorting capabilities
        options = {
            "limit": limit,
            "offset": offset,
            "sortBy": {
                "column": "created_at",
                "order": "asc"  # Get oldest files first
            }
        }
        response = client.storage.from_(bucket_name).list("", options)
        logger.info(f"Found {len(response)} files in current batch (offset: {offset})")
        return response
    except Exception as e:
        logger.error(f"Error listing files in bucket {bucket_name}: {str(e)}")
        return []

def delete_single_file(client: Client, bucket_name: str, file_name: str, max_retries: int = 3) -> bool:
    """
    Delete a single file with retry logic and verification.
    
    Parameters
    ----------
    client : Client
        Initialized Supabase client
    bucket_name : str
        Name of the storage bucket
    file_name : str
        Name of the file to delete
    max_retries : int
        Maximum number of retry attempts
        
    Returns
    -------
    bool
        True if file was successfully deleted, False otherwise
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to delete: {file_name} (attempt {attempt + 1}/{max_retries})")
            
            # Perform the delete operation
            delete_response = client.storage.from_(bucket_name).remove([file_name])
            logger.debug(f"Delete response: {delete_response}")
            
            # Add a small delay to allow the operation to complete
            time.sleep(0.5)
            
            # Verify the file is actually deleted by trying to get its metadata
            try:
                # Try to get the file info - this should fail if it's deleted
                file_info = client.storage.from_(bucket_name).list("", {
                    "limit": 1,
                    "search": file_name
                })
                
                # If we can still find the file, deletion may have failed
                if file_info and any(f['name'] == file_name for f in file_info):
                    logger.warning(f"File still exists after deletion attempt: {file_name}")
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying deletion in 2 seconds...")
                        time.sleep(2)
                        continue
                    else:
                        return False
                else:
                    logger.info(f"Successfully deleted: {file_name}")
                    return True
                    
            except Exception as verify_e:
                # If we can't find the file, it's likely deleted
                logger.info(f"File appears to be deleted (cannot verify): {file_name}")
                return True
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error deleting file {file_name} (attempt {attempt + 1}): {error_msg}")
            
            # Check for specific error types
            if "authentication" in error_msg.lower():
                logger.error("Authentication error - check your Supabase credentials")
                return False
            elif "permission" in error_msg.lower() or "forbidden" in error_msg.lower():
                logger.error("Permission error - check your storage bucket policies")
                return False
            elif "rate" in error_msg.lower() or "too many" in error_msg.lower():
                logger.warning("Rate limit detected - increasing delay")
                time.sleep(5)
            elif "connectionterminated" in error_msg.lower() or "connection" in error_msg.lower():
                logger.warning("Connection error detected - will retry with fresh connection")
                # Force a connection refresh on next operation by returning to caller
                raise Exception("Connection terminated - refresh needed")
            
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2  # Exponential backoff
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            
    return False

def delete_old_files(client: Client, cutoff_date: datetime, bucket_name: str = "incept-images", dry_run: bool = True) -> int:
    """
    Delete files created before the cutoff date.
    Uses pagination and rate limiting to process all files reliably.
    
    Parameters
    ----------
    client : Client
        Initialized Supabase client
    cutoff_date : datetime
        Files created before this date will be deleted
    bucket_name : str
        Name of the storage bucket
    dry_run : bool
        If True, only simulate deletion
        
    Returns
    -------
    int
        Number of files deleted
    """
    total_deleted_count = 0
    total_failed_count = 0
    batch_number = 1
    offset = 0
    batch_size = 50  # Smaller batch size for more reliable processing
    files_to_process = True
    operations_count = 0  # Track total operations to refresh connection
    
    while files_to_process:
        # Refresh connection every 1000 operations to prevent timeout
        if operations_count > 0 and operations_count % 1000 == 0:
            logger.info(f"Refreshing Supabase connection after {operations_count} operations...")
            client = get_supabase_client()
            time.sleep(2)  # Brief pause after reconnection
        
        logger.info(f"\nProcessing batch {batch_number} (offset: {offset}, operations: {operations_count})...")
        files = list_bucket_files(client, bucket_name, limit=batch_size, offset=offset)
        operations_count += 1  # Count the list operation
        
        if not files:
            logger.info("No more files found to process.")
            break
            
        # Track files to delete in this batch
        files_to_delete = []
        deleted_count = 0
        failed_count = 0
        
        # Print header for file list
        action = "Would delete" if dry_run else "Deleting"
        logger.info(f"\nListing files ({action} those before {cutoff_date.strftime('%Y-%m-%d')}):")
        logger.info("-" * 80)
        logger.info(f"{'Created At':<25} {'Size':<10} File Name")
        logger.info("-" * 80)
        
        for file in files:
            # Parse the created_at timestamp
            created_at = datetime.fromisoformat(file['created_at'].replace('Z', '+00:00'))
            
            # Format file size
            size_bytes = file.get('metadata', {}).get('size', 0)
            if size_bytes < 1024:
                size_str = f"{size_bytes}B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes/1024:.1f}KB"
            else:
                size_str = f"{size_bytes/(1024*1024):.1f}MB"
                
            # Print file info
            action_marker = " [TO DELETE] " if created_at < cutoff_date else " "
            logger.info(f"{created_at.strftime('%Y-%m-%d %H:%M:%S'):<25} {size_str:<10} {file['name']}{action_marker}")
            
            if created_at < cutoff_date:
                files_to_delete.append(file['name'])
        
        # Process deletions with rate limiting
        if files_to_delete and not dry_run:
            logger.info(f"\nDeleting {len(files_to_delete)} files with rate limiting...")
            
            for i, file_name in enumerate(files_to_delete):
                # Check if we need to refresh connection during deletion batch
                if operations_count > 0 and operations_count % 1000 == 0:
                    logger.info(f"Refreshing Supabase connection during deletions after {operations_count} operations...")
                    client = get_supabase_client()
                    time.sleep(2)
                
                try:
                    success = delete_single_file(client, bucket_name, file_name)
                    operations_count += 3  # Each delete involves: delete + verify + potential retry operations
                    
                    if success:
                        deleted_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    if "refresh needed" in str(e):
                        logger.info("Connection refresh needed - getting new client")
                        client = get_supabase_client()
                        time.sleep(2)
                        # Retry the operation with fresh connection
                        try:
                            success = delete_single_file(client, bucket_name, file_name)
                            operations_count += 3
                            if success:
                                deleted_count += 1
                            else:
                                failed_count += 1
                        except Exception as retry_e:
                            logger.error(f"Failed to delete {file_name} even after connection refresh: {retry_e}")
                            failed_count += 1
                    else:
                        logger.error(f"Unexpected error deleting {file_name}: {e}")
                        failed_count += 1
                
                # Rate limiting: pause between deletions
                if i < len(files_to_delete) - 1:  # Don't sleep after the last file
                    time.sleep(1)  # 1 second between deletions
                    
                # Progress update every 10 files
                if (i + 1) % 10 == 0:
                    logger.info(f"Progress: {i + 1}/{len(files_to_delete)} files processed (operations: {operations_count})")
        
        elif files_to_delete and dry_run:
            deleted_count = len(files_to_delete)
        
        logger.info("-" * 80)
        action = "Would delete" if dry_run else "Deleted"
        logger.info(f"{action} {deleted_count} files in batch {batch_number}")
        
        if failed_count > 0:
            logger.error(f"Failed to delete {failed_count} files in this batch")
        
        total_deleted_count += deleted_count
        total_failed_count += failed_count
        
        # Check if we should continue processing
        found_files_to_delete = len(files_to_delete) > 0
        
        # If we didn't find any files to delete in this batch and we got fewer files
        # than the batch size, we can stop processing
        if not found_files_to_delete and len(files) < batch_size:
            files_to_process = False
        
        # For actual deletions, reset offset to 0 since we deleted files
        # For dry runs, increment offset normally
        if dry_run:
            offset += batch_size
        else:
            # Only increment offset if we didn't delete any files
            if deleted_count == 0:
                offset += batch_size
            # Otherwise, keep offset at 0 since we removed files from the beginning
        
        batch_number += 1
        
        # If we're doing a dry run, no need to keep processing after first batch
        if dry_run:
            break
        
        # Add delay between batches to avoid overwhelming the API
        if files_to_process:
            logger.info("Waiting 3 seconds before next batch...")
            time.sleep(3)
    
    action = "Would delete" if dry_run else "Deleted"
    logger.info(f"\nSummary: {action} a total of {total_deleted_count} files created before {cutoff_date.strftime('%Y-%m-%d')}")
    
    if total_failed_count > 0:
        logger.error(f"Failed to delete {total_failed_count} files")
    
    if not dry_run:
        logger.info("\nNote: If files are not being deleted, please check:")
        logger.info("1. Your Supabase credentials (SUPABASE_URL and SUPABASE_KEY)")
        logger.info("2. Storage bucket permissions (RLS policies)")
        logger.info("3. Whether you're using an anon key (limited permissions) or service_role key (full access)")
        logger.info("4. Network connectivity and rate limits")
    
    return total_deleted_count

def main():
    parser = argparse.ArgumentParser(description="Clean up old files from Supabase storage bucket")
    parser.add_argument(
        "--cutoff-date",
        type=str,
        default="2025-08-10",
        help="Delete files created before this date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--bucket",
        type=str,
        default="incept-images",
        help="Supabase storage bucket name"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate deletion without actually deleting files"
    )
    
    args = parser.parse_args()
    
    try:
        # Convert cutoff date string to datetime
        cutoff_date = datetime.strptime(args.cutoff_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        
        # Initialize Supabase client
        client = get_supabase_client()
        
        # Delete old files
        deleted_count = delete_old_files(
            client=client,
            cutoff_date=cutoff_date,
            bucket_name=args.bucket,
            dry_run=args.dry_run
        )
        
        if args.dry_run:
            logger.info(f"Dry run completed. {deleted_count} files would be deleted.")
        else:
            logger.info(f"Cleanup completed. {deleted_count} files deleted.")
            
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main()) 