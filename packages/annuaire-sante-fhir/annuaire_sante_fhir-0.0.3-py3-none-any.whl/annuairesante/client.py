"""Core client for Annuaire Sante FHIR API."""

import os
from typing import Any, Optional
from urllib.parse import urljoin

import httpx

from .exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


class AnnuaireSanteClient:
    """Client for Annuaire Sante FHIR API.

    Args:
        api_key: API key for authentication. If not provided, will look for
                ANNUAIRE_SANTE_API_KEY environment variable.
        base_url: Base URL for the API. Defaults to production URL.
        timeout: Request timeout in seconds. Defaults to 30.
    """

    DEFAULT_BASE_URL = "https://gateway.api.esante.gouv.fr/fhir/v2"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        # Load environment variables if needed
        if api_key is None and not os.getenv("ANNUAIRE_SANTE_API_KEY"):
            try:
                from dotenv import load_dotenv

                load_dotenv()
            except ImportError:
                pass  # python-dotenv not installed

        self.api_key = api_key or os.getenv("ANNUAIRE_SANTE_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Provide it via api_key parameter or "
                "ANNUAIRE_SANTE_API_KEY environment variable."
            )

        self.base_url = base_url or self.DEFAULT_BASE_URL

        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.timeout = timeout

        # Initialize HTTP client
        self.http_client = httpx.Client(
            timeout=timeout,
            headers=self._get_headers(),
        )

        # Lazy-load resource wrappers
        self._practitioner: Any = None
        self._organization: Any = None
        self._practitioner_role: Any = None
        self._healthcare_service: Any = None
        self._device: Any = None

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "ESANTE-API-KEY": self.api_key or "",
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json",
        }

    def _build_url(self, path: str) -> str:
        """Build full URL from path."""
        # Ensure base_url ends with / and path doesn't start with /
        base = self.base_url.rstrip("/") + "/"
        path = path.lstrip("/")
        return urljoin(base, path)

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response and raise appropriate exceptions."""
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            raise AuthenticationError("Invalid API key or authentication failed")
        elif response.status_code == 404:
            raise NotFoundError("Resource not found")
        elif response.status_code == 400:
            raise ValidationError(f"Validation error: {response.text}")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        elif 500 <= response.status_code < 600:
            raise ServerError(f"Server error: {response.status_code} - {response.text}")
        else:
            raise Exception(f"Unexpected error: {response.status_code} - {response.text}")

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        """Make GET request to API.

        Args:
            path: API endpoint path
            params: Query parameters

        Returns:
            Parsed JSON response
        """
        url = self._build_url(path)
        response = self.http_client.get(url, params=params)
        return self._handle_response(response)

    def post(self, path: str, data: dict[str, Any]) -> Any:
        """Make POST request to API.

        Args:
            path: API endpoint path
            data: Request body

        Returns:
            Parsed JSON response
        """
        url = self._build_url(path)
        response = self.http_client.post(url, json=data)
        return self._handle_response(response)

    @property
    def practitioner(self) -> Any:
        """Get Practitioner resource wrapper.

        Returns:
            PractitionerResource instance

        Example:
            ```python
            # Search
            bundle = client.practitioner.search(family="MARTIN")

            # Iterate all results
            for pract in client.practitioner.search_all(family="MARTIN"):
                print(pract["id"])

            # Get by ID
            pract = client.practitioner.get("003-123456")
            ```
        """
        if self._practitioner is None:
            from .resources.practitioner import PractitionerResource

            self._practitioner = PractitionerResource(self)
        return self._practitioner

    @property
    def organization(self) -> Any:
        """Get Organization resource wrapper.

        Returns:
            OrganizationResource instance

        Example:
            ```python
            # Search
            bundle = client.organization.search(name="hopital")

            # Iterate all results
            for org in client.organization.search_all(address_city="Paris"):
                print(org["name"])

            # Get by ID
            org = client.organization.get("001-01-879996")
            ```
        """
        if self._organization is None:
            from .resources.organization import OrganizationResource

            self._organization = OrganizationResource(self)
        return self._organization

    @property
    def practitioner_role(self) -> Any:
        """Get PractitionerRole resource wrapper.

        Returns:
            PractitionerRoleResource instance
        """
        if self._practitioner_role is None:
            from .resources.practitioner_role import PractitionerRoleResource

            self._practitioner_role = PractitionerRoleResource(self)
        return self._practitioner_role

    @property
    def healthcare_service(self) -> Any:
        """Get HealthcareService resource wrapper.

        Returns:
            HealthcareServiceResource instance
        """
        if self._healthcare_service is None:
            from .resources.healthcare_service import HealthcareServiceResource

            self._healthcare_service = HealthcareServiceResource(self)
        return self._healthcare_service

    @property
    def device(self) -> Any:
        """Get Device resource wrapper.

        Returns:
            DeviceResource instance
        """
        if self._device is None:
            from .resources.device import DeviceResource

            self._device = DeviceResource(self)
        return self._device

    def metadata(self) -> Any:
        """Get CapabilityStatement (server metadata).

        Returns:
            CapabilityStatement resource
        """
        return self.get("/metadata")

    def close(self) -> None:
        """Close HTTP client."""
        self.http_client.close()

    def __enter__(self) -> "AnnuaireSanteClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
