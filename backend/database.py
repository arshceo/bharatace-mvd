"""
Database connection and utilities for Supabase.
"""

from supabase import create_client, Client
from settings import settings
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Wrapper class for Supabase client with connection management.
    """
    
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """
        Get or create a Supabase client instance (singleton pattern).
        
        Returns:
            Client: Initialized Supabase client
        """
        if cls._instance is None:
            try:
                cls._instance = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_KEY
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
                raise
        
        return cls._instance


def get_supabase() -> Client:
    """
    Dependency function to get Supabase client for FastAPI routes.
    
    Returns:
        Client: Supabase client instance
    """
    return SupabaseClient.get_client()


def get_supabase_admin() -> Client:
    """
    Get Supabase client with SERVICE_ROLE_KEY for admin operations.
    This bypasses RLS policies and should be used for tool operations.
    
    Returns:
        Client: Supabase client with admin privileges
    """
    return create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY
    )


# Table name constant
KNOWLEDGE_BASE_TABLE = "knowledge_base"
