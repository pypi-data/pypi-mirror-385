"""
Cloud Storage Module
Provides unified interface for AWS S3 and Azure Blob Storage
"""

from . import os_s3
from . import os_azure

__all__ = ['os_s3', 'os_azure']
