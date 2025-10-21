"""SynClub API client base class."""

import requests
from typing import Any, Dict
from synclub_mcp.exceptions import SynclubAuthError, SynclubRequestError

class SynclubAPIClient:
    """Base client for making requests to SynClub API."""
    
    def __init__(self, api_key: str, api_host: str):
        """Initialize the API client.
        
        Args:
            api_key: The API key for authentication
            api_host: The API host URL
        """
        self.api_key = api_key
        self.api_host = api_host
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'x-api-key': api_key,
            'MM-API-Source': 'synclub-mcp'
        })

    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Make an HTTP request to the SynClub API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            API response data as dictionary
            
        Raises:
            SynclubAuthError: If authentication fails
            SynclubRequestError: If the request fails
        """
        url = f"{self.api_host}{endpoint}"
        
        # Set Content-Type based on whether files are being uploaded
        files = kwargs.get('files')
        if not files:
            self.session.headers['Content-Type'] = 'application/json'
        else:
            # Remove Content-Type header for multipart/form-data
            # requests library will set it automatically with the correct boundary
            self.session.headers.pop('Content-Type', None)
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Check for other HTTP errors
            response.raise_for_status()
            
            data = response.json()
            
            # Check API-specific error codes
            base_resp = data.get("base_resp", {})
            print("!!!base_resp""")
            print(base_resp)
            if base_resp.get("status_code") != 0:
                match base_resp.get("status_code"):
                    case 1004:
                        raise SynclubAuthError(
                            f"API Error: {base_resp.get('status_msg')}, please check your API key and API host."
                            f"Trace-Id: {response.headers.get('Trace-Id')}"
                        )
                    case 2038:
                        raise SynclubRequestError(
                            f"API Error: {base_resp.get('status_msg')}, should complete real-name verification on the open-platform(https://synclub.baidu-int.com)."
                            f"Trace-Id: {response.headers.get('Trace-Id')}"
                        )
                    case _:
                        raise SynclubRequestError(
                            f"API Error: {base_resp.get('status_code')}-{base_resp.get('status_msg')} "
                            f"Trace-Id: {response.headers.get('Trace-Id')}"
                            f"base_resp Response: {str(base_resp)}"
                            f"raw Response: {str(data)}"
                        )
                
            return data
            
        except requests.exceptions.RequestException as e:
            raise SynclubRequestError(f"Request failed: {str(e)}")
            
    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a GET request."""
        return self._make_request("GET", endpoint, **kwargs)
        
    def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a POST request."""
        return self._make_request("POST", endpoint, **kwargs) 