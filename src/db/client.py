"""
Supabase database client.
"""
from supabase import create_client, Client
from src.core.config import settings
from src.core.logger import get_logger

logger = get_logger(__name__)

# Global Supabase client
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_key
)

logger.info(f"supabase_client_initialized: {settings.supabase_url}")
