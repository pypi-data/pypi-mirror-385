"""
AWS S3 Storage Module
Handles all S3 upload operations and client initialization
"""

import os
import time
import logging
from pathlib import Path
from urllib.parse import quote
from typing import Optional, Tuple

import boto3
from botocore.exceptions import ClientError

logger                   = logging.getLogger(__name__)

# Environment variables
AWS_ACCESS_KEY_ID        = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY    = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION               = os.getenv("AWS_REGION", "us-east-1")
AWS_S3_BUCKET            = os.getenv("AWS_S3_BUCKET")

# Configuration
UPLOAD_RETRY_COUNT       = 3
RETRY_DELAY_BASE         = 1

# Global client
s3_client                = None


def initialize_s3(file_backend_url: Optional[str] = None) -> bool:
    """
    Initialize S3 client if credentials are available.

    Args:
        file_backend_url: Optional base URL for building public URLs

    Returns:
        bool: True if initialized successfully, False otherwise
    """
    global s3_client

    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or not AWS_S3_BUCKET:
        logger.warning("S3 not configured (missing AWS credentials or bucket)")
        return False

    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        logger.info("S3 client initialized successfully")
        return True
    except ClientError as e:
        logger.error(f"S3 init error: {e}")
        s3_client = None
        return False


def is_initialized() -> bool:
    """Check if S3 client is initialized."""
    return s3_client is not None


def upload_to_s3(
    local_file_path: Path,
    s3_key: Optional[str] = None,
    max_retries: int = UPLOAD_RETRY_COUNT,
    file_backend_url: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Upload a file to S3.

    Args:
        local_file_path: Path to the local file
        s3_key: S3 object key (defaults to filename)
        max_retries: Number of retry attempts
        file_backend_url: Optional base URL for building public URLs

    Returns:
        Tuple of (success, public_url, s3_url)
    """
    if not s3_client:
        return False, None, None

    if not s3_key:
        s3_key = local_file_path.name

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"S3 upload attempt {attempt}/{max_retries}: {local_file_path} -> s3://{AWS_S3_BUCKET}/{s3_key}"
            )
            s3_client.upload_file(str(local_file_path), AWS_S3_BUCKET, s3_key)

            quoted_key = quote(s3_key)
            s3_url = f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{quoted_key}"

            # Build public URL if file_backend_url is provided
            if file_backend_url:
                public_url = f"{file_backend_url}/{quoted_key}"
            else:
                public_url = s3_url

            return True, public_url, s3_url

        except ClientError as e:
            logger.error(f"S3 upload failed on attempt {attempt}: {e}")
            if attempt < max_retries:
                time.sleep(RETRY_DELAY_BASE * (2 ** (attempt - 1)))

    # All retries failed
    quoted_key = quote(s3_key)
    expected_url = f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{quoted_key}"
    return False, None, expected_url


def get_s3_client():
    """Get the initialized S3 client."""
    return s3_client


def get_bucket_name() -> Optional[str]:
    """Get the configured S3 bucket name."""
    return AWS_S3_BUCKET


def get_region() -> str:
    """Get the configured AWS region."""
    return AWS_REGION
