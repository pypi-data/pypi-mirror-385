from .vfb_queries import *
from .solr_result_cache import get_solr_cache

# Caching enhancements (optional import - don't break if dependencies missing)
try:
    from .cache_enhancements import (
        enable_vfbquery_caching, 
        disable_vfbquery_caching,
        clear_vfbquery_cache,
        get_vfbquery_cache_stats,
        set_cache_ttl,
        set_cache_memory_limit,
        set_cache_max_items,
        enable_disk_cache,
        disable_disk_cache,
        get_cache_config,
        CacheConfig
    )
    from .cached_functions import (
        get_term_info_cached,
        get_instances_cached, 
        patch_vfbquery_with_caching,
        unpatch_vfbquery_caching
    )
    __caching_available__ = True
    
    # Enable caching by default with 3-month TTL and 2GB memory cache
    import os
    
    # Check if caching should be disabled via environment variable
    cache_disabled = os.getenv('VFBQUERY_CACHE_ENABLED', 'true').lower() in ('false', '0', 'no', 'off')
    
    if not cache_disabled:
        # Enable caching with VFB_connect-like defaults
        enable_vfbquery_caching(
            cache_ttl_hours=2160,      # 3 months (90 days)
            memory_cache_size_mb=2048, # 2GB memory cache
            max_items=10000,           # Max 10k items as safeguard
            disk_cache_enabled=True    # Persistent across sessions
        )
        
        # Automatically patch existing functions for transparent caching
        patch_vfbquery_with_caching()
        
        print("VFBquery: Caching enabled by default (3-month TTL, 2GB memory)")
        print("         Disable with: export VFBQUERY_CACHE_ENABLED=false")
    
except ImportError:
    __caching_available__ = False
    print("VFBquery: Caching not available (dependencies missing)")

# Convenience function for clearing SOLR cache entries
def clear_solr_cache(query_type: str, term_id: str) -> bool:
    """
    Clear a specific SOLR cache entry to force refresh
    
    Args:
        query_type: Type of query ('term_info', 'instances', etc.)
        term_id: Term identifier (e.g., 'FBbt_00003748')
    
    Returns:
        True if successfully cleared, False otherwise
    
    Example:
        >>> import vfbquery as vfb
        >>> vfb.clear_solr_cache('term_info', 'FBbt_00003748')
        >>> result = vfb.get_term_info('FBbt_00003748')  # Will fetch fresh data
    """
    cache = get_solr_cache()
    return cache.clear_cache_entry(query_type, term_id)

# SOLR-based result caching (experimental - for cold start optimization)
try:
    from .solr_cache_integration import (
        enable_solr_result_caching,
        disable_solr_result_caching, 
        warmup_solr_cache,
        get_solr_cache_stats as get_solr_cache_stats_func,
        cleanup_solr_cache
    )
    __solr_caching_available__ = True
except ImportError:
    __solr_caching_available__ = False

# Version information
__version__ = "0.4.1"
