"""
Secure API Client for Vanna Insight Engine
Handles JWT authentication and API communication with the FastAPI backend.
NO database credentials or internal backend variables are stored here.
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class VannaAPIClient:
    """
    Secure client for communicating with the Vanna Insight Engine backend.
    
    This client:
    - Handles JWT authentication via /auth/login endpoint
    - Manages token refresh and expiration
    - Attaches Bearer tokens to all API requests
    - Does NOT store any database credentials
    - Uses conditional debug authentication for development
    """

    def __init__(self, backend_url: Optional[str] = None, timeout: int = 30):
        """
        Initialize the API client.
        
        Args:
            backend_url: Backend URL (default: from BACKEND_URL env var)
            timeout: Request timeout in seconds
        """
        self.backend_url = backend_url or os.getenv("BACKEND_URL", "http://api:8000")
        self.timeout = timeout
        self.session = self._create_session()
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        self.debug_mode = os.getenv("DEBUG", "false").lower() == "true"

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        # Retry strategy: retry on connection errors, timeouts, and specific HTTP codes
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def _get_headers(self) -> Dict[str, str]:
        """Build request headers with authentication."""
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        return headers

    def is_token_valid(self) -> bool:
        """Check if the current token is still valid."""
        if not self.access_token or not self.token_expiry:
            return False
        return datetime.utcnow() < self.token_expiry

    def login(self, username: str, password: str) -> bool:
        """
        Authenticate with the backend and obtain a JWT token.
        
        Args:
            username: User's username/email
            password: User's password
            
        Returns:
            True if authentication was successful, False otherwise
        """
        try:
            endpoint = f"{self.backend_url}/api/v1/auth/login"
            payload = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                
                # Decode token to get expiry (optional but useful for debugging)
                if self.access_token:
                    try:
                        decoded = jwt.decode(
                            self.access_token,
                            options={"verify_signature": False}
                        )
                        if "exp" in decoded:
                            self.token_expiry = datetime.fromtimestamp(decoded["exp"])
                    except (jwt.DecodeError, jwt.InvalidTokenError):
                        # Token is valid even if we can't decode it locally
                        self.token_expiry = None
                
                return True
            else:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", error_msg)
                except json.JSONDecodeError:
                    pass
                
                print(f"Login failed: {response.status_code} - {error_msg}")
                return False
                
        except requests.RequestException as e:
            print(f"Connection error during login: {e}")
            return False

    def logout(self) -> None:
        """Clear authentication token."""
        self.access_token = None
        self.token_expiry = None

    def health_check(self) -> Dict[str, Any]:
        """
        Check backend health status.
        
        Returns:
            Health status response
        """
        try:
            endpoint = f"{self.backend_url}/health"
            response = self.session.get(
                endpoint,
                timeout=self.timeout
            )
            return response.json()
        except requests.RequestException as e:
            return {"status": "error", "message": str(e)}

    def generate_sql(self, question: str) -> Dict[str, Any]:
        """
        Generate SQL from a natural language question.
        
        Args:
            question: Natural language question
            
        Returns:
            Generated SQL and metadata
        """
        return self._make_request(
            "POST",
            "/api/v1/generate-sql",
            {"question": question}
        )

    def fix_sql(self, sql: str, error_msg: str) -> Dict[str, Any]:
        """
        Fix SQL based on an error message.

        Args:
            sql: The SQL that failed
            error_msg: The error message

        Returns:
            Fixed SQL and metadata
        """
        return self._make_request(
            "POST",
            "/api/v1/fix-sql",
            {"sql": sql, "error_msg": error_msg}
        )

    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """
        Validate SQL syntax and semantics.

        Args:
            sql: The SQL query to validate

        Returns:
            Validation result with is_valid flag and issues list
        """
        if not self.is_token_valid():
            return {"error": "Authentication required. Please log in first."}

        return self._make_request(
            "POST",
            "/api/v1/sql/validate",
            {"sql": sql}
        )

    def explain_sql(self, sql: str) -> Dict[str, Any]:
        """
        Explain SQL in natural language.
        
        Args:
            sql: The SQL query to explain
            
        Returns:
            Explanation and metadata
        """
        return self._make_request(
            "POST",
            "/api/v1/explain-sql",
            {"sql": sql}
        )

    def execute_sql(self, sql: str, question: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a SQL query (requires authentication).

        Args:
            sql: The SQL query to execute
            question: The original question (optional, defaults to sql)

        Returns:
            Query results and metadata
        """
        if not self.is_token_valid():
            return {"error": "Authentication required. Please log in first."}

        return self._make_request(
            "POST",
            "/api/v1/sql/execute",
            {"question": question or sql, "sql": sql}
        )

    def get_query_history(self) -> Dict[str, Any]:
        """
        Get user's query history (requires authentication).
        
        Returns:
            Dict with a ``queries`` list for
            compatibility with the UI renderer.
        """
        if not self.is_token_valid():
            return {"error": "Authentication required. Please log in first."}

        result = self._make_request("GET", "/api/v1/sql/history")

        # API may return a bare list or an object; normalize
        # to {"queries": [...]} so app.py can safely call .get().
        if isinstance(result, list):
            return {"queries": result}
        return result

    def submit_feedback(self, query_id: str, question: str, feedback: str, rating: int) -> Dict[str, Any]:
        """
        Submit feedback on a generated query.

        Args:
            query_id: ID of the query
            question: The original question
            feedback: User's feedback text
            rating: Rating (1-5)

        Returns:
            Feedback submission response
        """
        if not self.is_token_valid():
            return {"error": "Authentication required. Please log in first."}

        return self._make_request(
            "POST",
            "/api/v1/feedback",
            {
                "query_id": query_id,
                "question": question,
                "feedback": feedback,
                "rating": rating
            }
        )

    # ------------------------------------------------------------------
    # Admin / Planned Features
    # ------------------------------------------------------------------

    def get_feedback_metrics(self) -> Dict[str, Any]:
        """
        Get aggregated feedback metrics (planned feature).
        
        Returns:
            Planned feature response.
        """
        if not self.is_token_valid():
            return {"error": "Authentication required. Please log in first."}

        return self._make_request("GET", "/admin/feedback-metrics")

    def list_scheduled_reports(self) -> Dict[str, Any]:
        """
        List scheduled reports (planned feature).
        
        Returns:
            Planned feature response with scheduled_reports list.
        """
        if not self.is_token_valid():
            return {"error": "Authentication required. Please log in first."}

        return self._make_request("GET", "/admin/scheduled/list")

    def approve_sql_feature_info(self) -> Dict[str, Any]:
        """
        Request SQL approval feature information (planned feature).

        Returns:
            Planned feature response.
        """
        if not self.is_token_valid():
            return {"error": "Authentication required. Please log in first."}

        return self._make_request("POST", "/admin/approve-sql")

    def train_model(self, feedback_ids: Optional[list] = None) -> Dict[str, Any]:
        """
        Trigger model training on approved feedback.

        Args:
            feedback_ids: Optional list of specific feedback IDs to train on.
                        If None, uses all approved feedback.

        Returns:
            Training job response
        """
        if not self.is_token_valid():
            return {"error": "Authentication required. Please log in first."}

        payload = {}
        if feedback_ids:
            payload["feedback_ids"] = feedback_ids

        return self._make_request(
            "POST",
            "/api/v1/feedback/train",
            payload
        )

    def get_config(self) -> Dict[str, Any]:
        """
        Get runtime configuration (admin only).
        
        Returns:
            Configuration object
        """
        if not self.is_token_valid():
            return {"error": "Authentication required. Please log in first."}

        # Admin configuration lives at /admin/config in the backend.
        return self._make_request("GET", "/admin/config")

    def check_target_db_health(self) -> Dict[str, Any]:
        """
        Check Target (user) Database connectivity.

        Uses the /admin/db/target/health endpoint, which inspects the
        configured TARGET_DATABASE_URL (typically SQLite for demo/user data).
        """
        if not self.is_token_valid():
            return {"error": "Authentication required. Please log in first."}

        return self._make_request("GET", "/admin/db/target/health")

    def test_target_db_connection(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test connectivity to an arbitrary Target Database configuration.

        This calls the admin endpoint /admin/db/target/test with the supplied
        payload. Credentials are NOT persisted in the backend; they are used
        only for a one-off connectivity check.
        """
        if not self.is_token_valid():
            return {"error": "Authentication required. Please log in first."}

        return self._make_request("POST", "/admin/db/target/test", payload)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the backend.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body (for POST/PUT)
            
        Returns:
            Response JSON or error object
        """
        try:
            url = f"{self.backend_url}{endpoint}"
            headers = self._get_headers()
            
            if method.upper() == "GET":
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
            elif method.upper() == "POST":
                response = self.session.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
            elif method.upper() == "PUT":
                response = self.session.put(
                    url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
            elif method.upper() == "DELETE":
                response = self.session.delete(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
            else:
                return {"error": f"Unsupported HTTP method: {method}"}
            
            # Handle different response codes
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 401:
                self.logout()
                return {"error": "Unauthorized. Please log in again."}
            elif response.status_code == 403:
                return {"error": "Access denied."}
            elif response.status_code == 404:
                return {"error": "Endpoint not found."}
            else:
                try:
                    error_data = response.json()
                    return {"error": error_data.get("detail", str(response.text))}
                except json.JSONDecodeError:
                    return {"error": f"HTTP {response.status_code}: {response.text}"}
                    
        except requests.Timeout:
            return {"error": f"Request timeout after {self.timeout} seconds"}
        except requests.ConnectionError as e:
            return {"error": f"Connection error: {str(e)}"}
        except requests.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}


# Create a global client instance for Streamlit
def get_client() -> VannaAPIClient:
    """Get or create the global API client instance."""
    if "api_client" not in locals():
        globals()["api_client"] = VannaAPIClient()
    return globals()["api_client"]
