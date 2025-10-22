"""Base classes for API resources."""

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Optional, cast

if TYPE_CHECKING:
    from ..client import AnnuaireSanteClient


class Bundle:
    """Represents a FHIR Bundle with pagination support.

    A Bundle wraps a FHIR search response and provides easy access to:
    - Total count of matching resources (NOTE: API does not provide this, always 0)
    - Entries in the current page
    - Pagination (next, previous pages)
    - Iteration over all pages

    Note:
        The Annuaire Sante FHIR API does not include the 'total' field in Bundle
        responses, so bundle.total will always be 0. To count results, you must
        iterate through all pages.
    """

    def __init__(
        self, data: dict[str, Any], client: "AnnuaireSanteClient", resource: "BaseResource"
    ):
        """Initialize Bundle.

        Args:
            data: FHIR Bundle response
            client: API client for fetching next pages
            resource: Resource instance for making requests
        """
        self.data = data
        self.client = client
        self.resource = resource
        # NOTE: L'API Annuaire Sante ne fournit pas le champ 'total'
        self.total = data.get("total", 0)

        # Extract entries
        entries = data.get("entry", [])
        self.entries: list[dict[str, Any]] = [e["resource"] for e in entries if "resource" in e]

        # Extract pagination links
        self._links = {link["relation"]: link["url"] for link in data.get("link", [])}

    def has_next(self) -> bool:
        """Check if there is a next page.

        Returns:
            True if next page exists
        """
        return "next" in self._links

    def next(self) -> Optional["Bundle"]:
        """Fetch the next page.

        Returns:
            Bundle for next page, or None if no next page
        """
        if not self.has_next():
            return None

        # The next link is a full URL, use client.http_client directly
        next_url = self._links["next"]
        response = self.client.http_client.get(next_url)
        data = self.client._handle_response(response)
        return Bundle(data, self.client, self.resource)

    def has_previous(self) -> bool:
        """Check if there is a previous page.

        Returns:
            True if previous page exists
        """
        return "previous" in self._links

    def previous(self) -> Optional["Bundle"]:
        """Fetch the previous page.

        Returns:
            Bundle for previous page, or None if no previous page
        """
        if not self.has_previous():
            return None

        prev_url = self._links["previous"]
        response = self.client.http_client.get(prev_url)
        data = self.client._handle_response(response)
        return Bundle(data, self.client, self.resource)

    def iter_all_pages(self) -> Iterator["Bundle"]:
        """Iterate over all pages starting from current page.

        Yields:
            Bundle objects for each page
        """
        current: Optional[Bundle] = self
        while current is not None:
            yield current
            current = current.next()

    def iter_all(self) -> Iterator[dict[str, Any]]:
        """Iterate over all resources across all pages.

        This automatically handles pagination in the background.

        Yields:
            FHIR resources (dict)

        Example:
            ```python
            bundle = client.practitioner.search(family="MARTIN")
            for practitioner in bundle.iter_all():
                print(practitioner["id"])
            ```
        """
        for page in self.iter_all_pages():
            yield from page.entries

    def __len__(self) -> int:
        """Return number of entries in current page."""
        return len(self.entries)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Iterate over entries in current page only."""
        return iter(self.entries)

    def __repr__(self) -> str:
        return f"<Bundle total={self.total} entries={len(self.entries)}>"


class BaseResource:
    """Base class for API resources.

    Provides common methods for searching and retrieving resources.
    """

    resource_type: str = ""  # Override in subclasses (e.g., "Practitioner")

    def __init__(self, client: "AnnuaireSanteClient"):
        """Initialize resource.

        Args:
            client: API client instance
        """
        self.client = client

    @property
    def resource_path(self) -> str:
        """Get the API path for this resource (e.g., /Practitioner)."""
        return f"/{self.resource_type}"

    def search(self, **params: Any) -> Bundle:
        """Search for resources.

        Args:
            **params: Search parameters (see API documentation for available parameters)

        Returns:
            Bundle with search results

        Example:
            ```python
            # Search with pagination
            bundle = resource.search(family="MARTIN", _count=50)
            print(f"Found {bundle.total} results")

            for entry in bundle.entries:
                print(entry["id"])

            # Get next page if available
            if bundle.has_next():
                next_bundle = bundle.next()
            ```
        """
        response = self.client.get(self.resource_path, params=params)
        return Bundle(response, self.client, self)

    def search_all(self, **params: Any) -> Iterator[dict[str, Any]]:
        """Search and iterate over ALL matching resources (automatic pagination).

        This is a generator that automatically fetches all pages and yields
        individual resources. Useful for bulk operations.

        Args:
            **params: Search parameters

        Yields:
            FHIR resources (dict)

        Example:
            ```python
            # Iterate over ALL practitioners with family name MARTIN
            for practitioner in resource.search_all(family="MARTIN"):
                db.save(practitioner)
            ```

        Warning:
            Be careful with queries that return thousands of results.
            Consider adding filters or using _lastUpdated for incremental sync.
        """
        bundle = self.search(**params)
        yield from bundle.iter_all()

    def get(self, resource_id: str) -> dict[str, Any]:
        """Get a specific resource by ID.

        Args:
            resource_id: Resource ID

        Returns:
            FHIR resource

        Example:
            ```python
            practitioner = resource.get("003-123456")
            print(practitioner["name"])
            ```
        """
        return cast(dict[str, Any], self.client.get(f"{self.resource_path}/{resource_id}"))
