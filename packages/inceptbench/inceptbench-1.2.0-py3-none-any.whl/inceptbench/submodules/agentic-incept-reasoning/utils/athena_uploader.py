"""
Athena Database Uploader

This module handles authentication and uploading of educational content to the Athena database.
Uses AWS Cognito for authentication and GraphQL (AppSync) for API calls.
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
import requests

# Load environment variables from .env file in the same directory as this module
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Athena uploader: Loaded environment variables from {env_path}")
    else:
        # Fallback to system environment
        load_dotenv()
except ImportError:
    # python-dotenv not installed, rely on system environment variables
    pass

logger = logging.getLogger(__name__)

class AthenaUploader:
    """Handles uploading content to the Athena database with AWS Cognito authentication."""
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the Athena uploader.
        
        Parameters
        ----------
        username : str, optional
            AWS Cognito username. If not provided, uses ATHENA_USERNAME environment variable.
        password : str, optional
            AWS Cognito password. If not provided, uses ATHENA_PASSWORD environment variable.
        """
        # AWS Cognito configuration
        self.aws_region = "us-east-1"
        self.user_pool_id = "us-east-1_htk33cNuR"
        self.client_id = "5r0pt3s4635jmu3r96s59ttu6c"
        self.cognito_endpoint = f"https://cognito-idp.{self.aws_region}.amazonaws.com/"
        
        # GraphQL endpoint
        self.graphql_endpoint = "https://6h3av7224be6jfuu3z6sjl7tyu.appsync-api.us-east-1.amazonaws.com/graphql"
        
        # Authentication credentials
        self.username = username or os.getenv('ATHENA_USERNAME')
        self.password = password or os.getenv('ATHENA_PASSWORD')
        
        if not self.username or not self.password:
            logger.warning("No username/password provided for Athena uploader. "
                         "Set ATHENA_USERNAME and ATHENA_PASSWORD environment variables.")
        
        # Session for requests
        self.session = requests.Session()
        self.id_token = None
        self.token_expires_at = 0
    
    def _authenticate(self) -> str:
        """
        Authenticate with AWS Cognito and get an ID token.
        
        Returns
        -------
        str
            The ID token for API authentication
            
        Raises
        ------
        Exception
            If authentication fails
        """
        if not self.username or not self.password:
            raise Exception("Username and password required for authentication")
        
        # Check if we have a valid token
        if self.id_token and time.time() < self.token_expires_at:
            return self.id_token
        
        logger.debug("Authenticating with AWS Cognito...")
        
        headers = {
            'Content-Type': 'application/x-amz-json-1.1',
            'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth'
        }
        
        body = {
            "AuthFlow": "USER_PASSWORD_AUTH",
            "ClientId": self.client_id,
            "AuthParameters": {
                "USERNAME": self.username,
                "PASSWORD": self.password
            },
            "ClientMetadata": {}
        }
        
        try:
            response = self.session.post(
                self.cognito_endpoint,
                headers=headers,
                json=body,
                timeout=30
            )
            response.raise_for_status()
            
            auth_result = response.json().get('AuthenticationResult', {})
            self.id_token = auth_result.get('IdToken')
            
            if not self.id_token:
                raise Exception("No ID token received from Cognito")
            
            # Calculate token expiration (tokens typically last 1 hour, we'll refresh after 55 minutes)
            expires_in = auth_result.get('ExpiresIn', 3600)
            self.token_expires_at = time.time() + expires_in - 300  # 5 minute buffer
            
            logger.debug("Successfully authenticated with AWS Cognito")
            return self.id_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to authenticate with Cognito: {str(e)}")
            raise Exception(f"Authentication failed: {str(e)}")
    
    def _make_graphql_request(self, query: str, variables: Dict[str, Any], 
                             max_retries: int = 3) -> Dict[str, Any]:
        """
        Make a GraphQL request to the Athena API.
        
        Parameters
        ----------
        query : str
            The GraphQL query or mutation
        variables : dict
            Variables for the GraphQL query
        max_retries : int
            Maximum number of retry attempts
            
        Returns
        -------
        dict
            The response data from the GraphQL API
            
        Raises
        ------
        Exception
            If the request fails after all retries
        """
        for attempt in range(max_retries):
            try:
                # Get valid ID token
                id_token = self._authenticate()
                
                headers = {
                    'Authorization': id_token,
                    'Content-Type': 'application/json'
                }
                
                body = {
                    'query': query,
                    'variables': variables
                }
                
                logger.debug(f"GraphQL request (attempt {attempt + 1}/{max_retries})")
                
                response = self.session.post(
                    self.graphql_endpoint,
                    headers=headers,
                    json=body,
                    timeout=120
                )
                response.raise_for_status()
                
                response_data = response.json()
                
                # Check for GraphQL errors
                if 'errors' in response_data:
                    error_messages = [error.get('message', 'Unknown error') for error in response_data['errors']]
                    raise Exception(f"GraphQL errors: {'; '.join(error_messages)}")
                
                return response_data.get('data', {})
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    backoff_time = min(2 ** attempt, 10)
                    logger.warning(f"GraphQL request failed (attempt {attempt + 1}), "
                                 f"retrying in {backoff_time}s: {str(e)}")
                    time.sleep(backoff_time)
                    
                    # Clear token on 401/403 errors to force re-authentication
                    if hasattr(e, 'response') and e.response and e.response.status_code in [401, 403]:
                        self.id_token = None
                        self.token_expires_at = 0
                else:
                    logger.error(f"GraphQL request failed after {max_retries} attempts: {str(e)}")
                    raise Exception(f"GraphQL request failed: {str(e)}")
    
    def upload_content(self, athena_content: Dict[str, Any], curriculum_row, 
                      difficulty: Optional[str] = None) -> bool:
        """
        Upload structured content to the Athena database.
        
        Parameters
        ----------
        athena_content : dict
            The structured content in Athena format (MCQ or TextEntry schema)
        curriculum_row : CurriculumRow
            The curriculum information associated with this content
        difficulty : str, optional
            The difficulty level for questions ("easy", "medium", "hard")
            
        Returns
        -------
        bool
            True if upload was successful, False otherwise
        """
        try:
            # Convert content to JSON string as required by the API
            content_json = json.dumps(athena_content)
            
            # Use standard_id as platformStandardId (this maps the curriculum to the platform)
            platform_standard_id = curriculum_row.standard_id
            
            if not platform_standard_id:
                logger.error(f"No standard_id found for curriculum row: {curriculum_row.standard}")
                return False
            
            # Use content_generator_config_id from curriculum row
            content_generator_config_id = curriculum_row.content_generator_config_id
            
            if not content_generator_config_id:
                logger.error(f"No content_generator_config_id found for curriculum row: {curriculum_row.standard}")
                return False
            
            # Log the content we're trying to upload for debugging
            logger.debug(f"Athena content structure: {json.dumps(athena_content, indent=2)}")
            
            # Prepare the GraphQL mutation
            mutation = """
            mutation InsertContent($input: InsertContentInput!) {
              insertContent(input: $input) {
                platformGeneratedContentId
              }
            }
            """
            
            variables = {
                "input": {
                    "platformContentGeneratorConfigId": content_generator_config_id,
                    "platformStandardId": platform_standard_id,
                    "content": content_json,
                    "customAttributes": [
                        {
                            "attributeName": "grade",
                            "attributeValue": curriculum_row.grade
                        },
                        {
                            "attributeName": "subject", 
                            "attributeValue": curriculum_row.subject
                        },
                        {
                            "attributeName": "unit",
                            "attributeValue": curriculum_row.unit
                        },
                        {
                            "attributeName": "cluster",
                            "attributeValue": curriculum_row.cluster
                        },
                        {
                            "attributeName": "standard",
                            "attributeValue": curriculum_row.standard
                        },
                        {
                            "attributeName": "standard_description",
                            "attributeValue": curriculum_row.standard_description
                        },
                        {
                            "attributeName": "standard_extended_id",
                            "attributeValue": curriculum_row.standard_extended_id
                        },
                        {
                            "attributeName": "content_generator_config_id",
                            "attributeValue": content_generator_config_id
                        },
                        {
                            "attributeName": "generated_at",
                            "attributeValue": str(int(time.time()))
                        },
                        {
                            "attributeName": "source",
                            "attributeValue": "content_generator"
                        }
                    ]
                }
            }
            
            # Add difficulty attribute if provided (for questions)
            difficulty_used = None
            if "question" in athena_content:
                difficulty_used = difficulty or "medium"
            if difficulty_used:
                variables["input"]["customAttributes"].append({
                    "attributeName": "difficulty",
                    "attributeValue": difficulty_used
                })
            
            logger.debug(f"Uploading content for {curriculum_row.grade} {curriculum_row.subject}: "
                        f"{curriculum_row.standard}")
            
            # Make the GraphQL request
            response_data = self._make_graphql_request(mutation, variables)
            
            # Check if we got a valid response
            insert_result = response_data.get('insertContent', {})
            platform_generated_content_id = insert_result.get('platformGeneratedContentId')
            
            if platform_generated_content_id:
                logger.info(f"Successfully uploaded content with ID: {platform_generated_content_id}")
                return True
            else:
                logger.error("No platformGeneratedContentId returned from API")
                return False
                
        except Exception as e:
            # Log the content that failed to upload for debugging
            logger.error(f"Failed to upload content. Athena content was: {json.dumps(athena_content, indent=2)}")
            logger.error(f"Error uploading content to Athena: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test the connection to the Athena API by attempting authentication.
        
        Returns
        -------
        bool
            True if connection is successful, False otherwise
        """
        try:
            logger.info("Testing connection to Athena API...")
            
            # Try to authenticate
            id_token = self._authenticate()
            
            if id_token:
                logger.info("✓ Authentication successful")
                return True
            else:
                logger.error("✗ Authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to Athena API: {str(e)}")
            return False
    
    def get_upload_stats(self) -> Dict[str, Any]:
        """
        Get statistics about uploaded content.
        
        Note: This would require additional GraphQL queries to get actual stats.
        For now, returns basic connection status.
        
        Returns
        -------
        dict
            Statistics about the connection and upload capability
        """
        try:
            connected = self.test_connection()
            
            return {
                "connection_status": "connected" if connected else "disconnected",
                "graphql_endpoint": self.graphql_endpoint,
                "username": self.username if self.username else "not_configured"
            }
            
        except Exception as e:
            logger.error(f"Failed to get upload stats: {str(e)}")
            return {"error": str(e)}


# Convenience function for quick testing
def test_athena_connection() -> bool:
    """Test the connection to the Athena API."""
    uploader = AthenaUploader()
    return uploader.test_connection()


if __name__ == "__main__":
    # Simple test when run directly
    logging.basicConfig(level=logging.INFO)
    
    uploader = AthenaUploader()
    
    print("Testing Athena connection...")
    if uploader.test_connection():
        print("✓ Connection successful")
    else:
        print("✗ Connection failed")
    
    print("\nUpload stats:")
    stats = uploader.get_upload_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}") 