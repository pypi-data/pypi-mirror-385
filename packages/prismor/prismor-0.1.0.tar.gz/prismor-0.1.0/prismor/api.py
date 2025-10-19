"""API client for Prismor security scanning service."""

import os
import requests
from typing import Optional, Dict, Any


class PrismorAPIError(Exception):
    """Custom exception for Prismor API errors."""
    pass


class PrismorClient:
    """Client for interacting with Prismor API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Prismor API client.
        
        Args:
            api_key: Prismor API key. If not provided, will look for PRISMOR_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("PRISMOR_API_KEY")
        if not self.api_key:
            raise PrismorAPIError(
                "PRISMOR_API_KEY environment variable is not set. "
                "Please set it with: export PRISMOR_API_KEY=your_api_key"
            )
        
        self.base_url = "https://api.prismor.dev"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def normalize_repo_url(self, repo: str) -> str:
        """Normalize repository input to a full GitHub URL.
        
        Args:
            repo: Repository in format 'username/repo' or full GitHub URL
            
        Returns:
            Full GitHub repository URL
        """
        if repo.startswith("http://") or repo.startswith("https://"):
            return repo
        
        # Assume it's in username/repo format
        if "/" in repo:
            return f"https://github.com/{repo}"
        
        raise PrismorAPIError(
            f"Invalid repository format: {repo}. "
            "Please use 'username/repo' or full GitHub URL"
        )
    
    def scan(
        self,
        repo: str,
        vex: bool = False,
        sbom: bool = False,
        detect_secret: bool = False,
        fullscan: bool = False
    ) -> Dict[str, Any]:
        """Perform security scan on a GitHub repository.
        
        Args:
            repo: Repository URL or username/repo format
            vex: Enable vulnerability scanning
            sbom: Enable SBOM generation
            detect_secret: Enable secret detection
            fullscan: Enable all scan types
            
        Returns:
            Dictionary containing scan results
        """
        repo_url = self.normalize_repo_url(repo)
        
        # Prepare request payload
        payload = {
            "repo_url": repo_url,
            "vex": vex or fullscan,
            "sbom": sbom or fullscan,
            "detect_secret": detect_secret or fullscan,
            "fullscan": fullscan
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/scan",
                json=payload,
                headers=self.headers,
                timeout=300  # 5 minute timeout
            )
            
            if response.status_code == 401:
                raise PrismorAPIError("Invalid API key. Please check your PRISMOR_API_KEY.")
            
            if response.status_code == 404:
                raise PrismorAPIError("API endpoint not found. Please check the API URL.")
            
            if response.status_code >= 400:
                error_msg = response.json().get("error", "Unknown error")
                raise PrismorAPIError(f"API error: {error_msg}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            raise PrismorAPIError(
                "Request timed out. The repository scan is taking longer than expected."
            )
        except requests.exceptions.ConnectionError:
            raise PrismorAPIError(
                "Failed to connect to Prismor API. Please check your internet connection."
            )
        except requests.exceptions.RequestException as e:
            raise PrismorAPIError(f"Request failed: {str(e)}")

