# utils/cache.py
import functools
import hashlib
import json
import pickle
import os
from datetime import datetime, timedelta
from utils.logger import logger

# Create cache directory if it doesn't exist
os.makedirs("cache", exist_ok=True)

class Cache:
    """Simple file-based cache system"""
    
    def __init__(self, timeout=3600):
        """
        Initialize cache with timeout
        
        Args:
            timeout: Cache timeout in seconds (default 1 hour)
        """
        self.timeout = timeout
    
    def _get_cache_key(self, *args, **kwargs):
        """Generate a unique cache key based on arguments"""
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_path(self, key):
        """Get file path for cache key"""
        return f"cache/{key}.pickle"
    
    def get(self, key):
        """Get value from cache"""
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            
            # Check if cache is expired
            if datetime.now() > data['expiry']:
                os.remove(cache_path)
                return None
            
            return data['value']
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            return None
    
    def set(self, key, value):
        """Set value in cache"""
        cache_path = self._get_cache_path(key)
        
        try:
            data = {
                'value': value,
                'expiry': datetime.now() + timedelta(seconds=self.timeout)
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            
            return True
        except Exception as e:
            logger.error(f"Cache write error: {e}")
            return False

# Create cache decorator
def cached(timeout=3600):
    """
    Decorator to cache function results
    
    Args:
        timeout: Cache timeout in seconds
    """
    cache = Cache(timeout=timeout)
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if caching is enabled in config
            from config import CACHE_ENABLED
            if not CACHE_ENABLED:
                return func(*args, **kwargs)
            
            # Generate cache key
            cache_key = cache._get_cache_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result)
            
            return result
        
        return wrapper
    
    return decorator