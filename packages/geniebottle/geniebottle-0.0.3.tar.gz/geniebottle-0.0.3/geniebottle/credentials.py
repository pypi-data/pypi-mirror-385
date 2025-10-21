"""
Credentials Manager for Genie Bottle

Securely stores and retrieves API keys for various services.
Credentials are stored in ~/.geniebottle/credentials.json with restricted permissions.
"""

import json
import os
import stat
from pathlib import Path
from typing import Optional, Dict, List


class CredentialsManager:
    """Manages secure storage of API credentials."""

    # Supported services and their configuration
    SERVICES = {
        'openai': {
            'name': 'OpenAI',
            'description': 'ChatGPT, DALL-E, Whisper',
            'env_var': 'OPENAI_API_KEY',
            'key_prefix': 'sk-',
            'signup_url': 'https://platform.openai.com/signup',
            'keys_url': 'https://platform.openai.com/api-keys'
        },
        'stabilityai': {
            'name': 'Stability AI',
            'description': 'Stable Diffusion',
            'env_var': 'STABILITY_KEY',
            'key_prefix': 'sk-',
            'signup_url': 'https://platform.stability.ai/',
            'keys_url': 'https://platform.stability.ai/account/keys'
        },
        'huggingface': {
            'name': 'Hugging Face',
            'description': 'Transformers, Models',
            'env_var': 'HUGGINGFACE_TOKEN',
            'key_prefix': 'hf_',
            'signup_url': 'https://huggingface.co/join',
            'keys_url': 'https://huggingface.co/settings/tokens'
        }
    }

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the credentials manager.

        Args:
            config_dir: Optional custom config directory. Defaults to ~/.geniebottle
        """
        if config_dir is None:
            self.config_dir = Path.home() / '.geniebottle'
        else:
            self.config_dir = Path(config_dir)

        self.credentials_file = self.config_dir / 'credentials.json'
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist."""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
            # Set directory permissions to 0700 (owner only)
            if os.name != 'nt':  # Unix-like systems
                os.chmod(self.config_dir, stat.S_IRWXU)

    def _set_secure_permissions(self):
        """Set secure permissions on credentials file."""
        if not self.credentials_file.exists():
            return

        if os.name != 'nt':  # Unix-like systems (Linux, macOS)
            # Set file permissions to 0600 (owner read/write only)
            os.chmod(self.credentials_file, stat.S_IRUSR | stat.S_IWUSR)
        else:  # Windows
            # On Windows, we can use icacls to restrict access
            # This is a basic implementation; could be enhanced with pywin32
            try:
                import subprocess
                # Remove all inherited permissions and grant full control only to current user
                username = os.environ.get('USERNAME', os.environ.get('USER'))
                if username:
                    subprocess.run(
                        ['icacls', str(self.credentials_file), '/inheritance:r', '/grant:r', f'{username}:F'],
                        capture_output=True,
                        check=False
                    )
            except Exception:
                # If this fails, at least we tried
                pass

    def _load_credentials(self) -> Dict[str, str]:
        """Load credentials from file."""
        if not self.credentials_file.exists():
            return {}

        try:
            with open(self.credentials_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _save_credentials(self, credentials: Dict[str, str]):
        """Save credentials to file."""
        with open(self.credentials_file, 'w') as f:
            json.dump(credentials, f, indent=2)

        # Set secure permissions after writing
        self._set_secure_permissions()

    def save_key(self, service: str, api_key: str) -> bool:
        """
        Save an API key for a service.

        Args:
            service: Service identifier (e.g., 'openai', 'stabilityai')
            api_key: The API key to store

        Returns:
            True if successful, False otherwise
        """
        if not api_key or not api_key.strip():
            return False

        credentials = self._load_credentials()
        credentials[service.lower()] = api_key.strip()

        try:
            self._save_credentials(credentials)
            return True
        except Exception:
            return False

    def get_key(self, service: str) -> Optional[str]:
        """
        Get an API key for a service.

        Args:
            service: Service identifier (e.g., 'openai', 'stabilityai')

        Returns:
            The API key if found, None otherwise
        """
        credentials = self._load_credentials()
        return credentials.get(service.lower())

    def remove_key(self, service: str) -> bool:
        """
        Remove an API key for a service.

        Args:
            service: Service identifier (e.g., 'openai', 'stabilityai')

        Returns:
            True if key was removed, False if it didn't exist
        """
        credentials = self._load_credentials()
        service_lower = service.lower()

        if service_lower in credentials:
            del credentials[service_lower]
            self._save_credentials(credentials)
            return True

        return False

    def list_services(self) -> List[str]:
        """
        List all services with stored credentials.

        Returns:
            List of service identifiers that have stored credentials
        """
        credentials = self._load_credentials()
        return list(credentials.keys())

    def clear_all(self):
        """Remove all stored credentials."""
        if self.credentials_file.exists():
            self.credentials_file.unlink()

    def has_key(self, service: str) -> bool:
        """
        Check if a service has a stored credential.

        Args:
            service: Service identifier

        Returns:
            True if credential exists, False otherwise
        """
        return self.get_key(service) is not None

    @classmethod
    def get_service_info(cls, service: str) -> Optional[Dict]:
        """
        Get information about a service.

        Args:
            service: Service identifier

        Returns:
            Service info dict or None if not found
        """
        return cls.SERVICES.get(service.lower())

    @classmethod
    def get_all_services(cls) -> Dict[str, Dict]:
        """Get information about all supported services."""
        return cls.SERVICES.copy()
