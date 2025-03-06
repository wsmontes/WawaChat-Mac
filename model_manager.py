import os
import shutil
import json
from pathlib import Path
import huggingface_hub
from huggingface_hub import scan_cache_dir

class ModelManager:
    """Utility class to manage downloaded models and cache"""
    
    def __init__(self):
        # Get the default Hugging Face cache directory
        try:
            # Use the proper function to get the cache dir
            self.cache_dir = huggingface_hub.constants.HUGGINGFACE_HUB_CACHE
            
            # If not set, get from environment variable
            if not self.cache_dir:
                self.cache_dir = os.environ.get("TRANSFORMERS_CACHE")
                
            # If still not set, use default location
            if not self.cache_dir:
                home = Path.home()
                # Try common cache locations
                for cache_path in [
                    home / ".cache" / "huggingface",
                    home / ".huggingface" / "cache",
                ]:
                    if cache_path.exists():
                        self.cache_dir = str(cache_path)
                        break
                    
                # If no cache directory found, create one
                if not self.cache_dir:
                    self.cache_dir = str(home / ".cache" / "huggingface")
                    os.makedirs(self.cache_dir, exist_ok=True)
                    
            # Ensure it's a string
            self.cache_dir = str(self.cache_dir)
        except Exception as e:
            print(f"Error determining cache directory: {e}")
            # Fallback to a reasonable default
            home = Path.home()
            self.cache_dir = str(home / ".cache" / "huggingface")
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_cache_info(self):
        """Get information about the cache directory"""
        try:
            cache_info = scan_cache_dir(self.cache_dir)
            return cache_info
        except Exception as e:
            print(f"Error scanning cache directory: {e}")
            return None
    
    def get_downloaded_models(self):
        """Get a list of downloaded models with size information"""
        try:
            cache_info = self.get_cache_info()
            if not cache_info:
                return []
                
            models = []
            
            # Iterate through repositories
            for repo in cache_info.repos:
                if hasattr(repo, 'revisions'):
                    for rev in repo.revisions:
                        try:
                            # Get revision identifier from commit_hash attribute
                            revision = getattr(rev, 'commit_hash', "unknown")
                            
                            # Get size directly from the size_on_disk attribute
                            size_mb = getattr(rev, 'size_on_disk', 0) / (1024 * 1024)
                            
                            # Get last_modified directly
                            last_modified = getattr(rev, 'last_modified', None)
                            
                            # Get file information if available
                            files = []
                            if hasattr(rev, 'files'):
                                files = rev.files
                            
                            models.append({
                                "repo_id": repo.repo_id,
                                "revision": revision,
                                "size_mb": round(size_mb, 2),
                                "last_modified": last_modified.isoformat() if last_modified else "Unknown",
                                "files": files
                            })
                        except Exception as e:
                            # Add minimal info if we encounter an error
                            models.append({
                                "repo_id": repo.repo_id,
                                "revision": "unknown",
                                "size_mb": 0,
                                "last_modified": "Unknown",
                                "error": str(e)
                            })
            return models
        except Exception as e:
            print(f"Error getting downloaded models: {e}")
            return []
    
    def get_total_cache_size(self):
        """Get the total size of the cache in MB"""
        try:
            # Use the size_on_disk attribute of cache_info directly
            cache_info = self.get_cache_info()
            if cache_info and hasattr(cache_info, 'size_on_disk'):
                return round(cache_info.size_on_disk / (1024 * 1024), 2)  # Convert to MB
            
            # Fall back to manual calculation if the above doesn't work
            total_bytes = 0
            for dirpath, _, filenames in os.walk(self.cache_dir):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total_bytes += os.path.getsize(fp)
            
            return round(total_bytes / (1024 * 1024), 2)  # Convert to MB
        except Exception as e:
            print(f"Error calculating cache size: {e}")
            return 0
    
    def delete_model(self, repo_id, revision=None):
        """Delete a specific model from the cache"""
        try:
            huggingface_hub.delete_from_cache(repo_id, revision=revision)
            return True, f"Successfully deleted {repo_id} ({revision})"
        except Exception as e:
            return False, f"Error deleting model: {e}"
    
    def clear_entire_cache(self):
        """Clear the entire cache directory"""
        try:
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
                os.makedirs(self.cache_dir)
            return True, "Cache cleared successfully"
        except Exception as e:
            return False, f"Error clearing cache: {e}"
    
    def export_models_info(self, file_path):
        """Export information about downloaded models to a JSON file"""
        try:
            models = self.get_downloaded_models()
            with open(file_path, 'w') as f:
                json.dump(models, f, indent=2)
            return True, f"Model information exported to {file_path}"
        except Exception as e:
            return False, f"Error exporting model information: {e}"


if __name__ == "__main__":
    # Example usage
    manager = ModelManager()
    print(f"Cache directory: {manager.cache_dir}")
    print(f"Total cache size: {manager.get_total_cache_size()} MB")
    
    models = manager.get_downloaded_models()
    for model in models:
        print(f"Model: {model['repo_id']} ({model['revision']}) - {model['size_mb']} MB")
