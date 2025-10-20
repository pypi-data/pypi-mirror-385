import logging
import os
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional, Union

import requests
from dotenv import find_dotenv, load_dotenv
from supabase import Client, create_client

# Load environment variables
load_dotenv(find_dotenv())

# Configure logging
logger = logging.getLogger(__name__)

# Supabase error messages
SUPABASE_ENV_VARS_ERROR = "SUPABASE_URL and SUPABASE_KEY environment variables must be set."
SUPABASE_UPLOAD_ERROR = SUPABASE_ENV_VARS_ERROR + " to upload images."
SUPABASE_QUERY_ERROR = SUPABASE_ENV_VARS_ERROR + " to query Supabase."
CONVERSATION_MESSAGE_ORDER_PRECISION = 1000

# IP geolocation cache - shared across requests with 24-hour expiry
_ip_location_cache: Dict[str, Dict[str, Any]] = {}
_cache_lock = threading.RLock()

def get_supabase_client() -> Client:
    """
    Initialize and return a Supabase client using environment variables.
    
    Returns
    -------
    Client
        The initialized Supabase client
        
    Raises
    ------
    RuntimeError
        If SUPABASE_URL or SUPABASE_KEY environment variables are not set
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise RuntimeError(SUPABASE_ENV_VARS_ERROR)

    return create_client(supabase_url, supabase_key)

def upload_image_to_supabase(
    image_bytes: bytes, 
    content_type: str = "image/png", 
    bucket_name: str = "incept-images",
    file_extension: str = ".png"
) -> str:
    """
    Upload image bytes to Supabase storage and return the public URL.
    
    Parameters
    ----------
    image_bytes : bytes
        The image data as bytes
    content_type : str, default "image/png"
        The MIME type of the image
    bucket_name : str, default "incept-images"
        The Supabase bucket to upload to
    file_extension : str, default ".png"
        The file extension to use
        
    Returns
    -------
    str
        The public URL of the uploaded image
    """
    supabase = get_supabase_client()
    
    # Generate unique filename
    file_name = f"{uuid.uuid4().hex}{file_extension}"
    
    # Write image bytes to a temporary file and upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        tmp_file.write(image_bytes)
        tmp_file_path = tmp_file.name
    
    try:
        upload_response = supabase.storage.from_(bucket_name).upload(
            file_name, 
            tmp_file_path, 
            {"content-type": content_type}
        )
    finally:
        # Ensure temporary file is removed regardless of upload outcome
        try:
            os.remove(tmp_file_path)
        except FileNotFoundError:
            pass
            
    # Retrieve and return the public URL of the uploaded file
    public_url = supabase.storage.from_(bucket_name).get_public_url(upload_response.path)
    # Wait 3s to ensure the file is uploaded and ready to be accessed
    time.sleep(3)
    return public_url

def delete_files_from_supabase(
    file_urls: Union[str, list[str]], 
    delay_seconds: float = 0.0,
    bucket_name: str = "incept-images"
) -> None:
    """
    Delete one or more files from Supabase storage after a delay, running in background threads.
    
    This function returns immediately while deletions happen in the background.
    Each file deletion waits for the specified delay before executing.
    
    Parameters
    ----------
    file_urls : Union[str, list[str]]
        Single file URL or list of file URLs to delete
    delay_seconds : float, default 5.0
        Number of seconds to wait before each deletion
    bucket_name : str, default "incept-images"
        The Supabase bucket containing the files
    """
    # Handle both single URL and list of URLs
    if isinstance(file_urls, str):
        urls_to_delete = [file_urls]
    else:
        urls_to_delete = file_urls
    
    if not urls_to_delete:
        return
    
    logger.info(f"Scheduling deletion of {len(urls_to_delete)} files in {delay_seconds} seconds")
    
    def delete_single_file(url: str):
        """Helper function to delete a single file."""
        try:
            # Wait for the specified delay
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            
            supabase = get_supabase_client()
            
            # Extract the file path from the public URL
            # URLs are typically in format: https://...supabase.co/storage/v1/object/public/bucket-name/filename
            if "/object/public/" in url:
                # Extract filename from URL
                url_parts = url.split("/object/public/")
                if len(url_parts) > 1:
                    # Remove bucket name and get just the filename
                    path_with_bucket = url_parts[1]
                    # Remove the bucket name prefix and any query parameters
                    file_path = path_with_bucket.split("/", 1)
                    if len(file_path) > 1:
                        filename = file_path[1].split("?")[0]  # Remove query parameters if present
                    else:
                        filename = path_with_bucket.split("?")[0]
                else:
                    logger.error(f"Could not extract filename from URL: {url}")
                    return
            else:
                logger.error(f"Invalid Supabase URL format: {url}")
                return
            
            # Delete the file
            supabase.storage.from_(bucket_name).remove([filename])
            
            logger.info(f"Successfully deleted file from Supabase: {filename}")
            
        except Exception as e:
            logger.error(f"Error deleting {url}: {e}")
    
    # Start daemon threads for background deletion
    for url in urls_to_delete:
        thread = threading.Thread(target=delete_single_file, args=(url,), daemon=True)
        thread.start()

def upload_video_to_supabase(
    video_bytes: bytes, 
    content_type: str = "video/mp4", 
    bucket_name: str = "incept-videos",
    file_extension: str = ".mp4"
) -> str:
    """
    Upload video bytes to Supabase storage and return the public URL.
    
    Parameters
    ----------
    video_bytes : bytes
        The video data as bytes
    content_type : str, default "video/mp4"
        The MIME type of the video
    bucket_name : str, default "incept-videos"
        The Supabase bucket to upload to (defaults to incept-videos for videos)
    file_extension : str, default ".mp4"
        The file extension to use
        
    Returns
    -------
    str
        The public URL of the uploaded video
    """
    supabase = get_supabase_client()
    
    # Generate unique filename
    file_name = f"{uuid.uuid4().hex}{file_extension}"
    
    # Write video bytes to a temporary file and upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        tmp_file.write(video_bytes)
        tmp_file_path = tmp_file.name
    
    try:
        upload_response = supabase.storage.from_(bucket_name).upload(
            file_name, 
            tmp_file_path, 
            {"content-type": content_type}
        )
    finally:
        # Ensure temporary file is removed regardless of upload outcome
        try:
            os.remove(tmp_file_path)
        except FileNotFoundError:
            pass
            
    # Retrieve and return the public URL of the uploaded file
    public_url = supabase.storage.from_(bucket_name).get_public_url(upload_response.path)
    # Wait 3s to ensure the file is uploaded and ready to be accessed
    time.sleep(3)
    return public_url

def upload_file_to_supabase(
    file_bytes: bytes, 
    content_type: str,
    bucket_name: str = "incept-images",
    file_extension: str = None
) -> str:
    """
    Upload file bytes to Supabase storage and return the public URL.
    
    Parameters
    ----------
    file_bytes : bytes
        The file data as bytes
    content_type : str
        The MIME type of the file (e.g., "text/html", "application/pdf")
    bucket_name : str
        The Supabase bucket to upload to
    file_extension : str, optional
        The file extension to use. If not provided, will be inferred from content_type
        
    Returns
    -------
    str
        The public URL of the uploaded file
    """
    supabase = get_supabase_client()
    
    # Infer file extension from content type if not provided
    if not file_extension:
        content_type_to_ext = {
            "text/html": ".html",
            "text/plain": ".txt",
            "application/pdf": ".pdf",
            "application/json": ".json",
            "text/css": ".css",
            "text/javascript": ".js",
            "application/xml": ".xml"
        }
        file_extension = content_type_to_ext.get(content_type, ".txt")
    
    # Generate unique filename
    file_name = f"{uuid.uuid4().hex}{file_extension}"
    
    # Write file bytes to a temporary file and upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
        tmp_file.write(file_bytes)
        tmp_file_path = tmp_file.name
    
    try:
        upload_response = supabase.storage.from_(bucket_name).upload(
            file_name, 
            tmp_file_path, 
            {"content-type": content_type}
        )
    finally:
        # Ensure temporary file is removed regardless of upload outcome
        try:
            os.remove(tmp_file_path)
        except FileNotFoundError:
            pass
            
    # Retrieve and return the public URL of the uploaded file
    public_url = supabase.storage.from_(bucket_name).get_public_url(upload_response.path)
    # Wait 3s to ensure the file is uploaded and ready to be accessed
    time.sleep(3)
    return public_url

def query_supabase_table(table_name: str, select_query: str = "*") -> list:
    """
    Query a Supabase table and return the results.
    
    Parameters
    ----------
    table_name : str
        The name of the table to query
    select_query : str, default "*"
        The columns to select from the table
        
    Returns
    -------
    list
        List of rows returned from the query
        
    Raises
    ------
    RuntimeError
        If there's an error fetching data from Supabase
    """
    client = get_supabase_client()

    try:
        resp = client.table(table_name).select(select_query).execute()
    except Exception as e:
        raise RuntimeError(f"Error querying Supabase table '{table_name}': {e}") from e

    return resp.data or []  # type: ignore[attr-defined] 

async def create_request_log(
    request_id: str,
    prompt: str,
    model: str,
    api_version: str,
    client_ip: str = None,
    user_agent: str = None,
    location_data: Dict[str, Any] = None
) -> bool:
    """
    Create a new request log entry in the incept_request_logs table.
    
    Parameters
    ----------
    request_id : str
        Unique identifier for the request
    prompt : str
        The user's prompt
    model : str
        The model used ('incept' or 'o3')
    api_version : str
        The API version
    client_ip : str, optional
        The client's IP address
    user_agent : str, optional
        The client's user agent string
    location_data : Dict[str, Any], optional
        Location information derived from IP (city, region, country, etc.)
        
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        data = {
            "request_id": request_id,
            "prompt": prompt,
            "model": model,
            "api_version": api_version
        }
        
        # Add optional user identification fields
        if client_ip:
            data["client_ip"] = client_ip
        if user_agent:
            data["user_agent"] = user_agent
        if location_data:
            data["location_data"] = location_data
        
        supabase.table("incept_request_logs").insert(data).execute()
        logger.info(
            f"Created request log for {request_id} with API version {api_version} from "
            f"IP {client_ip}"
        )
        return True
        
    except Exception as e:
        logger.error(f"Error creating request log for {request_id}: {str(e)}")
        return False

async def update_request_log_response(
    request_id: str,
    final_response: str,
    reasoning: str,
    response_time: float = None
) -> bool:
    """
    Update a request log with the final response and reasoning.
    
    Parameters
    ----------
    request_id : str
        Unique identifier for the request
    final_response : str
        The final response text
    reasoning : str
        The accumulated reasoning text
    response_time : float, optional
        The response time in milliseconds
        
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        data = {
            "final_response": final_response,
            "reasoning": reasoning,
            "updated_at": "now()"
        }
        
        # Add response time if provided
        if response_time is not None:
            data["response_time"] = response_time
        
        supabase.table("incept_request_logs").update(data).eq("request_id", request_id).execute()
        logger.info(
            f"Updated request log response for {request_id} (response time: {response_time}s)"
        )
        return True
        
    except Exception as e:
        logger.error(f"Error updating request log response for {request_id}: {str(e)}")
        return False

async def update_request_log_evaluation(
    request_id: str,
    evaluation_result: Dict[str, Any]
) -> bool:
    """
    Update a request log with evaluation results.
    
    Parameters
    ----------
    request_id : str
        Unique identifier for the request
    evaluation_result : Dict[str, Any]
        The evaluation result as a dictionary
        
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        data = {
            "evaluation_result": evaluation_result,
            "updated_at": "now()"
        }
        
        supabase.table("incept_request_logs").update(data).eq("request_id", request_id).execute()
        logger.info(f"Updated request log evaluation for {request_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating request log evaluation for {request_id}: {str(e)}")
        return False

async def update_request_log_feedback(
    request_id: str,
    rating: int = None,
    comments: str = None
) -> bool:
    """
    Update a request log with user feedback (rating and comments).
    
    Parameters
    ----------
    request_id : str
        Unique identifier for the request
    rating : int, optional
        User rating: 1 (positive), 0 (neutral), or -1 (negative)
    comments : str, optional
        User comments about the response
        
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        data = {
            "updated_at": "now()"
        }
        
        # Only update fields that were provided
        if rating is not None:
            # Validate rating is one of the allowed values
            if rating not in [-1, 0, 1]:
                logger.error(
                    f"Invalid rating value {rating} for {request_id}. Must be -1, 0, or 1."
                )
                return False
            data["rating"] = rating
            
        if comments is not None:
            data["comments"] = comments
        
        result = supabase.table("incept_request_logs").update(data).eq("request_id", request_id) \
            .execute()
        
        # Check if any rows were updated
        if hasattr(result, 'data') and len(result.data) == 0:
            logger.warning(f"No request log found for {request_id} to update feedback")
            return False
            
        logger.info(
            f"Updated request log feedback for {request_id} (rating: {rating}, comments: "
            f"{'provided' if comments else 'none'})"
        )
        return True
        
    except Exception as e:
        logger.error(f"Error updating request log feedback for {request_id}: {str(e)}")
        return False

async def update_request_log_simple_qc(
    request_id: str,
    qc_passed: bool,
    qc_reason: str,
    screenshot_url: str = None
) -> bool:
    """
    Update a request log with simple QC results.
    
    Parameters
    ----------
    request_id : str
        Unique identifier for the request
    qc_passed : bool
        Whether the simple QC check passed
    qc_reason : str
        Detailed reason/explanation from the QC check
    screenshot_url : str, optional
        URL of the uploaded screenshot
        
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        current_time = datetime.now(timezone.utc).isoformat()
        
        qc_result_data = {
            "passed": qc_passed,
            "reason": qc_reason,
            "screenshot_url": screenshot_url,
            "timestamp": current_time
        }
        
        data = {
            "simple_qc_result": qc_result_data,
            "updated_at": current_time
        }
        
        result = supabase.table("incept_request_logs").update(data).eq("request_id", request_id) \
            .execute()
        
        # Check if any rows were updated
        if hasattr(result, 'data') and len(result.data) == 0:
            logger.warning(f"No request log found for {request_id} to update simple QC")
            return False
            
        logger.info(
            f"Updated request log simple QC for {request_id} (passed: {qc_passed}, screenshot: "
            f"{'yes' if screenshot_url else 'no'})"
        )
        return True
        
    except Exception as e:
        logger.error(f"Error updating request log simple QC for {request_id}: {str(e)}")
        return False

async def find_request_by_content(content: str) -> Optional[str]:
    """
    Find a request ID by matching the final response content.
    This is a fallback method when request_id is not provided to evaluation.
    
    Parameters
    ----------
    content : str
        The content to match against final_response
        
    Returns
    -------
    Optional[str]
        The request_id if found, None otherwise
    """
    try:
        supabase = get_supabase_client()
        
        # Search for exact match first
        result = supabase.table("incept_request_logs").select("request_id") \
            .eq("final_response", content).execute()
        
        if result.data:
            logger.info("Found exact content match for evaluation")
            return result.data[0]["request_id"]
            
        # If no exact match, we could implement fuzzy matching here if needed
        logger.warning("No exact content match found for evaluation")
        return None
        
    except Exception as e:
        logger.error(f"Error finding request by content: {str(e)}")
        return None

async def get_request_log(request_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a request log by request_id.
    
    Parameters
    ----------
    request_id : str
        Unique identifier for the request
        
    Returns
    -------
    Optional[Dict[str, Any]]
        The request log data if found, None otherwise
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("incept_request_logs").select("*").eq("request_id", request_id) \
            .execute()
        
        if result.data:
            return result.data[0]
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving request log for {request_id}: {str(e)}")
        return None

async def find_successful_retry_record(request_id: str) -> str:
    """
    Find the successful retry record for a request that may have been retried.
    
    When a request times out and is retried, we create new records with IDs like
    request_id_retry_1, request_id_retry_2, etc. This function checks if any retry
    records exist and returns the ID of the first one that has a final response
    (not an error). If no successful retry is found, returns the original request_id.
    
    This ensures evaluations are logged to the record that actually contains the
    successful response, not the original failed attempt.
    
    Parameters
    ----------
    request_id : str
        The original request ID (may or may not have retries)
        
    Returns
    -------
    str
        The request_id to use for logging (either original or a retry ID)
    """
    try:
        # Check up to 5 retry attempts (exceeding our max_retries in server.py)
        for retry_num in range(1, 6):
            retry_id = f"{request_id}_retry_{retry_num}"
            retry_log = await get_request_log(retry_id)
            
            if retry_log:
                # Check if this retry has a final response (not an error)
                # A successful response will have a final_response that doesn't start with "[ERROR]"
                final_response = retry_log.get("final_response", "")
                if final_response and not final_response.startswith("[ERROR]"):
                    logger.info(
                        f"Found successful retry record {retry_id} for original request {request_id}"
                    )
                    return retry_id
            else:
                # No more retries exist, stop checking
                break
        
        # No successful retry found, use original request_id
        return request_id
        
    except Exception as e:
        logger.error(f"Error finding retry records for {request_id}: {str(e)}")
        # On error, fall back to original request_id
        return request_id 

async def get_location_from_ip(ip_address: str) -> Optional[Dict[str, Any]]:
    """
    Get location information from an IP address using a free geolocation service.
    Uses in-memory caching with 24-hour expiry to reduce API calls.
    
    Parameters
    ----------
    ip_address : str
        The IP address to look up
        
    Returns
    -------
    Optional[Dict[str, Any]]
        Location data including city, region, country, etc. or None if lookup fails
    """
    if not ip_address or ip_address in ['127.0.0.1', 'localhost', '::1']:
        return None
    
    # Check cache first
    with _cache_lock:
        if ip_address in _ip_location_cache:
            cached_entry = _ip_location_cache[ip_address]
            cache_age = datetime.now(timezone.utc) - cached_entry['timestamp']
            
            if cache_age < timedelta(hours=24):
                logger.debug(f"Using cached location data for IP {ip_address}")
                return cached_entry['data']
            else:
                # Cache expired, remove entry
                del _ip_location_cache[ip_address]
                logger.debug(f"Cache expired for IP {ip_address}, fetching new data")
    
    try:
        # Using ipapi.co free service (1000 requests/day limit)
        # Alternative services: ip-api.com, ipinfo.io, etc.
        response = requests.get(
            f"https://ipapi.co/{ip_address}/json/",
            timeout=5,
            headers={'User-Agent': 'Educational-Content-API/1.0'}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant fields and clean up the data
            location_data = {
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country_name"),
                "country_code": data.get("country_code"),
                "timezone": data.get("timezone"),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "org": data.get("org"),  # ISP/Organization
                "postal": data.get("postal")
            }
            
            # Remove None values
            location_data = {k: v for k, v in location_data.items() if v is not None}
            
            # Cache the result
            with _cache_lock:
                _ip_location_cache[ip_address] = {
                    'data': location_data,
                    'timestamp': datetime.now(timezone.utc)
                }
                logger.debug(f"Cached location data for IP {ip_address}")
            
            return location_data
            
        else:
            logger.warning(
                f"Failed to get location for IP {ip_address}: HTTP {response.status_code}"
            )
            return None
            
    except requests.RequestException as e:
        logger.warning(f"Error getting location for IP {ip_address}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting location for IP {ip_address}: {str(e)}")
        return None 

# ================================================================
# Conversation Management Functions
# ================================================================

async def create_conversation(user_id: str = None,
metadata: Dict[str, Any] = None) -> Optional[str]:
    """
    Create a new conversation record.
    
    Parameters
    ----------
    user_id : str, optional
        The user ID to associate with this conversation
    metadata : Dict[str, Any], optional
        Additional metadata to store with the conversation
        
    Returns
    -------
    Optional[str]
        The conversation_id if successful, None otherwise
    """
    try:
        supabase = get_supabase_client()
        
        data = {
            "conversation_id": str(uuid.uuid4()),
        }
        
        if user_id:
            data["user_id"] = user_id
        if metadata:
            data["metadata"] = metadata
        
        result = supabase.table("incept_conversations").insert(data).execute()
        
        if result.data:
            conversation_id = result.data[0]["conversation_id"]
            logger.info(f"Created conversation {conversation_id} for user {user_id}")
            return conversation_id
        
        return None
        
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}")
        return None

async def get_or_create_conversation_base_timestamp(conversation_id: str) -> Optional[float]:
    """
    Get the base timestamp for a conversation, or create one if this is the first message.
    
    Parameters
    ----------
    conversation_id : str
        The conversation ID
        
    Returns
    -------
    Optional[float]
        The base timestamp for the conversation, or None if error
    """
    try:
        supabase = get_supabase_client()
        
        # Get current conversation metadata
        result = supabase.table("incept_conversations").select("metadata") \
            .eq("conversation_id", conversation_id).execute()
        
        if not result.data:
            logger.error(f"Conversation {conversation_id} not found when getting base timestamp")
            return None
        
        metadata = result.data[0].get("metadata", {}) or {}
        base_timestamp = metadata.get("base_timestamp")
        
        if base_timestamp is None:
            # This is the first message - create and store base timestamp
            base_timestamp = datetime.now(timezone.utc).timestamp()
            metadata["base_timestamp"] = base_timestamp
            
            # Update the conversation metadata
            update_result = supabase.table("incept_conversations").update({
                "metadata": metadata
            }).eq("conversation_id", conversation_id).execute()
            
            if not update_result.data:
                logger.error(f"Failed to store base timestamp for conversation {conversation_id}")
                return None
                
            logger.info(
                f"Created base timestamp {base_timestamp} for conversation {conversation_id}"
            )
        
        return base_timestamp
        
    except Exception as e:
        logger.error(
            f"Error getting/creating base timestamp for conversation {conversation_id}: {str(e)}"
        )
        return None

async def save_conversation_message(
    conversation_id: str,
    role: str,
    content: str,
    message_order: int = None
) -> bool:
    """
    Save a message to a conversation.
    
    Parameters
    ----------
    conversation_id : str
        The conversation ID
    role : str
        The role of the message sender ('system', 'user', 'assistant')
    content : str
        The message content
    message_order : int, optional
        The order of the message in the conversation (auto-calculated if not provided)
        
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        # Use conversation-specific timestamp-based ordering to avoid race conditions
        if message_order is None:
            # Get or create the base timestamp for this conversation
            base_timestamp = await get_or_create_conversation_base_timestamp(conversation_id)
            
            if base_timestamp is None:
                # Fallback to simple ordering if base timestamp fails
                logger.warning(
                    f"Could not get base timestamp for conversation {conversation_id}, "
                    "using count-based ordering"
                )
                count_result = supabase.table("incept_conversation_messages") \
                    .select("message_id", count="exact").eq("conversation_id", conversation_id) \
                    .execute()
                message_order = (count_result.count or 0) + 1
            else:
                current_timestamp = datetime.now(timezone.utc).timestamp()
                # Use deciseconds (0.1s precision) offset from conversation start
                # This ensures first message is 1, and subsequent messages increase from there
                offset_seconds = current_timestamp - base_timestamp
                if offset_seconds < 0:
                    # Handle clock skew - use order 1 for negative offsets
                    message_order = 1
                else:
                    # Use round() instead of int() to handle floating point precision issues
                    # Add 1 to ensure first message gets order 1 (not 0)
                    message_order = round(offset_seconds * CONVERSATION_MESSAGE_ORDER_PRECISION) + 1
        
        data = {
            "message_id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "message_order": message_order
        }
        
        result = supabase.table("incept_conversation_messages").insert(data).execute()
        
        if result.data:
            logger.info(
                f"Saved {role} message to conversation {conversation_id} (order: {message_order})"
            )
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error saving message to conversation {conversation_id}: {str(e)}")
        return False

async def get_conversation_messages(
    conversation_id: str,
    limit: int = None,
    offset: int = 0
) -> list[Dict[str, Any]]:
    """
    Retrieve messages from a conversation.
    
    Parameters
    ----------
    conversation_id : str
        The conversation ID
    limit : int, optional
        Maximum number of messages to retrieve
    offset : int, default 0
        Number of messages to skip from the beginning
        
    Returns
    -------
    list[Dict[str, Any]]
        List of message records ordered by message_order
    """
    try:
        supabase = get_supabase_client()
        
        query = supabase.table("incept_conversation_messages").select("*") \
            .eq("conversation_id", conversation_id).order("message_order")
        
        if offset > 0:
            query = query.range(offset, offset + (limit - 1) if limit else 1000000)
        elif limit:
            query = query.limit(limit)
            
        result = query.execute()
        
        messages = result.data or []
        return messages
        
    except Exception as e:
        logger.error(f"Error retrieving messages from conversation {conversation_id}: {str(e)}")
        return []

async def get_recent_conversation_messages(
    conversation_id: str,
    limit: int = 10
) -> list[Dict[str, Any]]:
    """
    Retrieve the most recent messages from a conversation.
    
    Parameters
    ----------
    conversation_id : str
        The conversation ID
    limit : int, default 10
        Maximum number of recent messages to retrieve
        
    Returns
    -------
    list[Dict[str, Any]]
        List of recent message records ordered by message_order (most recent last)
    """
    try:
        supabase = get_supabase_client()
        
        # Get the most recent messages by getting the highest message_order values
        result = supabase.table("incept_conversation_messages").select("*") \
            .eq("conversation_id", conversation_id).order("message_order", desc=True).limit(limit) \
            .execute()
        
        messages = result.data or []
        # Reverse to get chronological order (oldest first)
        messages.reverse()
        
        return messages
        
    except Exception as e:
        logger.error(
            f"Error retrieving recent messages from conversation {conversation_id}: {str(e)}"
        )
        return []

async def conversation_exists(conversation_id: str) -> bool:
    """
    Check if a conversation exists.
    
    Parameters
    ----------
    conversation_id : str
        The conversation ID to check
        
    Returns
    -------
    bool
        True if conversation exists, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        result = supabase.table("incept_conversations").select("conversation_id") \
            .eq("conversation_id", conversation_id).execute()
        
        exists = bool(result.data)
        logger.info(f"Conversation {conversation_id} {'exists' if exists else 'does not exist'}")
        return exists
        
    except Exception as e:
        logger.error(f"Error checking if conversation {conversation_id} exists: {str(e)}")
        return False

async def update_conversation_metadata(
    conversation_id: str,
    metadata: Dict[str, Any]
) -> bool:
    """
    Update conversation metadata.
    
    Parameters
    ----------
    conversation_id : str
        The conversation ID
    metadata : Dict[str, Any]
        Metadata to update
        
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        data = {
            "metadata": metadata,
            "updated_at": "now()"
        }
        
        result = supabase.table("incept_conversations").update(data) \
            .eq("conversation_id", conversation_id).execute()
        
        if result.data:
            logger.info(f"Updated metadata for conversation {conversation_id}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error updating metadata for conversation {conversation_id}: {str(e)}")
        return False

async def delete_conversation(conversation_id: str) -> bool:
    """
    Delete a conversation and all its messages.
    
    Parameters
    ----------
    conversation_id : str
        The conversation ID to delete
        
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        # Delete messages first (due to foreign key constraint)
        supabase.table("incept_conversation_messages").delete() \
            .eq("conversation_id", conversation_id).execute()
        
        # Delete conversation
        supabase.table("incept_conversations").delete().eq("conversation_id", conversation_id) \
            .execute()
        
        logger.info(f"Deleted conversation {conversation_id} and its messages")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id}: {str(e)}")
        return False

async def save_conversation_message_with_cached_timestamp(
    conversation_id: str,
    role: str,
    content: str,
    base_timestamp: float,
    message_order: int = None
) -> bool:
    """
    Save a message to a conversation using a cached base timestamp.
    
    This avoids database hits for getting the base timestamp on every message save.
    
    Parameters
    ----------
    conversation_id : str
        The conversation ID
    role : str
        The role of the message sender ('system', 'user', 'assistant')
    content : str
        The message content
    base_timestamp : float
        The cached base timestamp for this conversation
    message_order : int, optional
        The order of the message (auto-calculated if not provided)
        
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        # Calculate message order using provided base timestamp
        if message_order is None:
            current_timestamp = datetime.now(timezone.utc).timestamp()
            offset_seconds = current_timestamp - base_timestamp
            if offset_seconds < 0:
                # Handle clock skew
                message_order = 1
            else:
                # Use round() to handle floating point precision
                message_order = round(offset_seconds * CONVERSATION_MESSAGE_ORDER_PRECISION) + 1
        
        data = {
            "message_id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "message_order": message_order
        }
        
        result = supabase.table("incept_conversation_messages").insert(data).execute()
        
        if result.data:
            logger.info(
                f"Saved {role} message to conversation {conversation_id} (order: {message_order})"
            )
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error saving message to conversation {conversation_id}: {str(e)}")
        return False

async def save_function_call_with_output_atomic_cached(
    conversation_id: str,
    function_name: str,
    arguments: str | dict,
    call_id: str,
    output: str,
    base_timestamp: float
) -> bool:
    """
    Atomically save a function call and its output using cached base timestamp.
    
    This avoids database hits for getting the base timestamp on every save.
    
    Parameters
    ----------
    conversation_id : str
        The conversation ID
    function_name : str
        The function name
    arguments : str | dict
        The function arguments
    call_id : str
        The call ID linking the function call to its output
    output : str
        The function output
    base_timestamp : float
        The cached base timestamp for this conversation
        
    Returns
    -------
    bool
        True if both function call and output were saved successfully, False otherwise
    """
    try:
        import json
        
        current_timestamp = datetime.now(timezone.utc).timestamp()
        # Use deciseconds offset from conversation start, ensuring order >= 1
        offset_seconds = current_timestamp - base_timestamp
        # Use round() instead of int() to handle floating point precision issues
        base_order = max(1, round(offset_seconds * CONVERSATION_MESSAGE_ORDER_PRECISION) + 1)
        
        # Prepare function call data
        call_data = {
            "name": function_name,
            "arguments": arguments,
            "call_id": call_id
        }
        
        # Prepare output data
        output_data = {
            "call_id": call_id,
            "output": output
        }
        
        # Save function call first with specific order using cached timestamp
        function_call_saved = await save_conversation_message_with_cached_timestamp(
            conversation_id, 
            "function_call", 
            json.dumps(call_data),
            base_timestamp,
            base_order
        )
        
        if not function_call_saved:
            logger.error(f"Failed to save function call for {call_id}")
            return False
        
        # Save output immediately after with incremented order to ensure sequencing
        output_saved = await save_conversation_message_with_cached_timestamp(
            conversation_id, 
            "function_call_output", 
            json.dumps(output_data),
            base_timestamp,
            base_order + 1
        )
        
        if not output_saved:
            logger.error(f"Failed to save function output for {call_id}")
            # TODO: Could implement rollback logic here if needed
            return False
        
        logger.info(f"Atomically saved function call and output for {call_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error in atomic save for function call {call_id}: {str(e)}")
        return False

async def save_function_call_with_output_atomic(
    conversation_id: str,
    function_name: str,
    arguments: str | dict,
    call_id: str,
    output: str
) -> bool:
    """
    Atomically save a function call and its output to prevent mismatches.
    
    This is the legacy function that hits the database for base timestamp.
    Use save_function_call_with_output_atomic_cached for better performance.
    
    Parameters
    ----------
    conversation_id : str
        The conversation ID
    function_name : str
        The function name
    arguments : str | dict
        The function arguments
    call_id : str
        The call ID linking the function call to its output
    output : str
        The function output
        
    Returns
    -------
    bool
        True if both function call and output were saved successfully, False otherwise
    """
    try:
        # Get conversation-specific base timestamp for consistent ordering
        conversation_base_timestamp = await \
            get_or_create_conversation_base_timestamp(conversation_id)
        
        if conversation_base_timestamp is None:
            logger.error(f"Could not get base timestamp for conversation {conversation_id}")
            return False
        
        # Use the cached version for better performance
        return await save_function_call_with_output_atomic_cached(
            conversation_id, function_name, arguments, call_id, output, conversation_base_timestamp
        )
        
    except Exception as e:
        logger.error(f"Error in atomic save for function call {call_id}: {str(e)}")
        return False

 