
import json
import hashlib
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

class SimpleCache:
    """
    A simple file-based semantic cache for long-running operations.
    Useful for: Search results, PDF extraction, Summary generation.
    """
    
    def __init__(self, cache_dir: str = ".cache", ttl_minutes: int = 60 * 24):
        self.cache_dir = Path(cache_dir)
        self.ttl_minutes = ttl_minutes
        self._ensure_dir()

    def _ensure_dir(self):
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, key: str) -> Path:
        """Generate a hashed filename for the key"""
        # Create a stable hash of the key
        key_hash = hashlib.md5(key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve item from cache if valid"""
        path = self._get_path(key)
        
        if not path.exists():
            return None
            
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            
            # Check TTL
            timestamp = data.get("_timestamp", 0)
            now = datetime.now().timestamp()
            age_minutes = (now - timestamp) / 60
            
            if age_minutes > self.ttl_minutes:
                # Expired
                path.unlink()
                return None
                
            return data["payload"]
            
        except Exception as e:
            # If corrupted, delete
            print(f"Cache read error: {e}")
            if path.exists():
                path.unlink()
            return None

    def set(self, key: str, value: Any):
        """Save item to cache"""
        path = self._get_path(key)
        
        cache_data = {
            "_timestamp": datetime.now().timestamp(),
            "payload": value
        }
        
        try:
            path.write_text(json.dumps(cache_data, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"Cache write error: {e}")

    def clear(self):
        """Clear the entire cache"""
        if self.cache_dir.exists():
            shutil.rmtree(str(self.cache_dir))
            self._ensure_dir()

# Singleton instance for global usage
cache = SimpleCache(cache_dir=".agent_cache")
