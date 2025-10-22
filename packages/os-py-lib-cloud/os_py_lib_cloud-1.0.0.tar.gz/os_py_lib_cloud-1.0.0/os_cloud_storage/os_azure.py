"""
Azure Blob Storage Module
Handles all Azure Blob Storage upload operations and client initialization
"""

import os
import time
import logging
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
from typing import Optional, Tuple

import requests
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

logger                          = logging.getLogger(__name__)

# Environment variables
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME            = os.getenv("AZURE_CONTAINER_NAME")

# Configuration
UPLOAD_RETRY_COUNT              = 3
RETRY_DELAY_BASE                = 1
CDN_READY_RETRY_COUNT           = 32
CDN_READY_DELAY                 = 2

# Global clients
blob_service_client             = None
container_client                = None


def initialize_azure(file_backend_url: Optional[str] = None) -> bool:
    """
    Initialize Azure Blob Storage client if credentials are available.

    Args:
        file_backend_url: Optional base URL for building public URLs

    Returns:
        bool: True if initialized successfully, False otherwise
    """
    global blob_service_client, container_client

    if not AZURE_STORAGE_CONNECTION_STRING:
        logger.warning("Azure Blob Storage not configured (missing connection string)")
        return False

    try:
        logger.info("Initializing Azure Blob Storage connection...")
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

        # Verify connection
        containers = list(blob_service_client.list_containers(results_per_page=1))
        logger.info(f"Azure connection successful. Found {len(containers)} containers.")

        # Get or create container
        try:
            container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
            container_client.get_container_properties()
            logger.info(f"Using existing Azure container: {AZURE_CONTAINER_NAME}")
        except (ResourceNotFoundError, ValueError) as e:
            if AZURE_CONTAINER_NAME == "$web":
                logger.warning("$web container not found or inaccessible; please create it via Azure Portal.")
                container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)
            else:
                container_client = blob_service_client.create_container(
                    AZURE_CONTAINER_NAME,
                    public_access="container"
                )
                logger.info(f"Created Azure container: {AZURE_CONTAINER_NAME}")

        return True

    except Exception as e:
        logger.error(f"Failed to initialize Azure Blob Storage: {str(e)}")
        blob_service_client = None
        container_client = None
        return False


def is_initialized() -> bool:
    """Check if Azure Blob Storage client is initialized."""
    return blob_service_client is not None and container_client is not None


def upload_to_azure(
    local_file_path: Path,
    blob_name: Optional[str] = None,
    max_retries: int = UPLOAD_RETRY_COUNT,
    file_backend_url: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Upload a file to Azure Blob Storage.

    Args:
        local_file_path: Path to the local file
        blob_name: Blob name (defaults to filename)
        max_retries: Number of retry attempts
        file_backend_url: Optional base URL for building public URLs

    Returns:
        Tuple of (success, public_url, blob_url)
    """
    if not blob_service_client or not container_client:
        logger.error("Azure Blob Storage not initialized. Ensure connection string is correct.")
        return False, None, None

    if not blob_name:
        blob_name = local_file_path.name

    # Determine blob path based on container type
    if AZURE_CONTAINER_NAME == "$web":
        blob_path = blob_name
    else:
        date_prefix = datetime.now().strftime("%Y/%m/%d")
        blob_path = f"{date_prefix}/{blob_name}"

    blob_client = blob_service_client.get_blob_client(
        container=AZURE_CONTAINER_NAME,
        blob=blob_path
    )

    for attempt in range(max_retries):
        try:
            if not os.path.exists(local_file_path):
                logger.error(f"Local file not found: {local_file_path}")
                return False, None, None

            with open(local_file_path, "rb") as data:
                logger.info(f"Uploading {local_file_path} to Azure as {blob_path}…")
                blob_client.upload_blob(data, overwrite=True)

            # Verify upload
            blob_client.get_blob_properties()
            url = blob_client.url
            logger.info(f"Successfully uploaded to Azure, URL={url}")

            # Verify CDN availability
            for i in range(CDN_READY_RETRY_COUNT):
                try:
                    resp = requests.get(url, headers={"Range": "bytes=0-10239"}, timeout=5)
                    if resp.status_code in (200, 206) and resp.content:
                        logger.info(f"Blob is now HTTP-accessible at {url}")
                        break
                except Exception as e:
                    logger.debug(f"Waiting for blob HTTP availability: {e}")
                time.sleep(CDN_READY_DELAY)
            else:
                logger.warning(f"Blob still not HTTP-ready after {CDN_READY_RETRY_COUNT} attempts")

            # Build public URL if file_backend_url is provided
            quoted_key = quote(blob_name)
            if file_backend_url:
                public_url = f"{file_backend_url}/{quoted_key}"
            else:
                public_url = url

            return True, public_url, url

        except Exception as e:
            logger.error(f"Azure upload failed attempt {attempt+1}/{max_retries}: {e}")
            time.sleep(RETRY_DELAY_BASE * (2 ** attempt))

    logger.error(f"Failed to upload {local_file_path} to Azure after {max_retries} attempts")
    return False, None, None


def get_blob_service_client():
    """Get the initialized blob service client."""
    return blob_service_client


def get_container_client():
    """Get the initialized container client."""
    return container_client


def get_container_name() -> Optional[str]:
    """Get the configured container name."""
    return AZURE_CONTAINER_NAME
