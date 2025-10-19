import requests
import json
from typing import Dict, Optional
from .config import get_base_url, get_api_key


class TngHttpClient:
    """HTTP client for TNG API communication"""
    
    def __init__(self):
        # Use centralized configuration manager
        self.base_url = get_base_url()
        self.api_key = get_api_key()
        
    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to TNG API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Get version dynamically
        try:
            from . import __version__
            version = __version__
        except ImportError:
            version = "0.1.0"  # fallback
            
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': f'TNG-Python/{version}'
        }
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"HTTP request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {e}")
            return None
    
    def ping(self) -> Optional[Dict]:
        """Call the ping endpoint to get version information"""
        return self._make_request('ping')
    
    def get_api_version(self) -> Optional[str]:
        """Get the API version from ping endpoint"""
        ping_response = self.ping()
        if ping_response and 'current_version' in ping_response:
            return ping_response['current_version'].get('pip_version')
        return None
    
    def validate_api_key(self) -> bool:
        """Validate API key by making an authenticated request"""
        if not self.api_key:
            return False
        
        response = self._make_request('ping')
        return response is not None


def get_http_client() -> TngHttpClient:
    """Get HTTP client instance"""
    return TngHttpClient()
