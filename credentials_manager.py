import os
import json
import keyring
from pathlib import Path
import base64

class CredentialsManager:
    """Manager for handling API credentials securely"""
    
    # Service name used for keyring
    SERVICE_NAME = "WawaChat"
    
    def __init__(self):
        """Initialize the credentials manager"""
        self.config_dir = self._get_config_dir()
        self.config_file = os.path.join(self.config_dir, "config.json")
        self._ensure_config_dir()
        
        # Default configuration
        self.config = {
            "use_keyring": True,
            "api_key_stored": False,
            "first_run_completed": False
        }
        
        # Load configuration
        self.load_config()
    
    def _get_config_dir(self):
        """Get the configuration directory path"""
        home_dir = Path.home()
        
        if os.name == 'nt':  # Windows
            config_dir = os.path.join(home_dir, "AppData", "Local", "WawaChat")
        else:  # macOS, Linux, etc.
            config_dir = os.path.join(home_dir, ".config", "wawachat")
            
        return config_dir
    
    def _ensure_config_dir(self):
        """Ensure the configuration directory exists"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
        except Exception as e:
            print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def set_api_key(self, api_key):
        """Store the API key either in keyring or config"""
        try:
            if not api_key:
                return False, "API key cannot be empty"
                
            if self.config.get("use_keyring", True):
                # Store in system keyring
                keyring.set_password(self.SERVICE_NAME, "huggingface_api_key", api_key)
            else:
                # Store in config file (less secure, but works everywhere)
                self.config["encrypted_api_key"] = self._simple_encrypt(api_key)
            
            self.config["api_key_stored"] = True
            self.save_config()
            return True, "API key saved successfully"
        except Exception as e:
            return False, f"Failed to store API key: {e}"
    
    def get_api_key(self):
        """Retrieve the API key"""
        if not self.config.get("api_key_stored", False):
            return None
            
        try:
            if self.config.get("use_keyring", True):
                # Get from system keyring
                return keyring.get_password(self.SERVICE_NAME, "huggingface_api_key")
            else:
                # Get from config file
                encrypted_key = self.config.get("encrypted_api_key")
                if encrypted_key:
                    return self._simple_decrypt(encrypted_key)
            return None
        except Exception as e:
            print(f"Error retrieving API key: {e}")
            return None
    
    def delete_api_key(self):
        """Delete the stored API key"""
        try:
            if self.config.get("use_keyring", True):
                keyring.delete_password(self.SERVICE_NAME, "huggingface_api_key")
            
            if "encrypted_api_key" in self.config:
                del self.config["encrypted_api_key"]
                
            self.config["api_key_stored"] = False
            self.save_config()
            return True, "API key deleted successfully"
        except Exception as e:
            return False, f"Failed to delete API key: {e}"
    
    def set_keyring_preference(self, use_keyring):
        """Set whether to use system keyring or config file"""
        # If changing from file storage to keyring or vice versa, and key exists, migrate it
        current_key = self.get_api_key()
        
        self.config["use_keyring"] = use_keyring
        self.save_config()
        
        if current_key and self.config.get("api_key_stored", False):
            # Re-save the key with the new storage method
            return self.set_api_key(current_key)
        
        return True, "Storage preference updated"
    
    def mark_first_run_completed(self):
        """Mark the first run wizard as completed"""
        self.config["first_run_completed"] = True
        self.save_config()
    
    def is_first_run(self):
        """Check if this is the first time running the app"""
        return not self.config.get("first_run_completed", False)
    
    def has_api_key(self):
        """Check if an API key is stored"""
        return self.config.get("api_key_stored", False)
    
    def _simple_encrypt(self, text):
        """Very simple obfuscation (not secure, just to avoid plaintext)"""
        # This is not secure encryption, just basic obfuscation
        return base64.b64encode(text.encode()).decode()
    
    def _simple_decrypt(self, encoded_text):
        """Reverse the simple obfuscation"""
        try:
            return base64.b64decode(encoded_text.encode()).decode()
        except:
            return None
