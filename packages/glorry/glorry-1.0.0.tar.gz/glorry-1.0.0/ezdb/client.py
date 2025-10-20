"""
Python client for EzDB REST API
"""
import requests
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class EzDBClient:
    """
    Python client for interacting with EzDB REST API server.

    Example:
        client = EzDBClient("http://localhost:8000")
        client.insert(vector=[0.1, 0.2, 0.3], metadata={"text": "Hello"})
        results = client.search(vector=[0.1, 0.2, 0.3], top_k=5)
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        collection: str = "default",
        timeout: int = 30
    ):
        """
        Initialize EzDB client.

        Args:
            base_url: Base URL of EzDB server
            collection: Default collection name
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.collection = collection
        self.timeout = timeout
        self.session = requests.Session()

    def _request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def health(self) -> Dict[str, Any]:
        """
        Check server health.

        Returns:
            Health status information
        """
        return self._request("GET", "/health")

    def create_collection(
        self,
        name: str,
        dimension: int,
        metric: str = "cosine",
        index_type: str = "hnsw"
    ) -> Dict[str, Any]:
        """
        Create a new collection.

        Args:
            name: Collection name
            dimension: Vector dimension
            metric: Similarity metric
            index_type: Index type

        Returns:
            Creation response
        """
        return self._request(
            "POST",
            "/collections",
            json_data={
                "name": name,
                "dimension": dimension,
                "metric": metric,
                "index_type": index_type
            }
        )

    def list_collections(self) -> List[str]:
        """
        List all collections.

        Returns:
            List of collection names
        """
        response = self._request("GET", "/collections")
        return response["collections"]

    def delete_collection(self, name: str) -> Dict[str, Any]:
        """
        Delete a collection.

        Args:
            name: Collection name

        Returns:
            Deletion response
        """
        return self._request("DELETE", f"/collections/{name}")

    def insert(
        self,
        vector: List[float],
        metadata: Optional[Dict[str, Any]] = None,
        id: Optional[str] = None,
        collection: Optional[str] = None
    ) -> str:
        """
        Insert a vector.

        Args:
            vector: Vector to insert
            metadata: Optional metadata
            id: Optional custom ID
            collection: Collection name (uses default if not specified)

        Returns:
            ID of inserted vector
        """
        collection = collection or self.collection
        response = self._request(
            "POST",
            f"/collections/{collection}/insert",
            json_data={
                "vector": vector,
                "metadata": metadata,
                "id": id
            }
        )
        return response["id"]

    def insert_batch(
        self,
        vectors: List[List[float]],
        metadata_list: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        collection: Optional[str] = None
    ) -> List[str]:
        """
        Insert multiple vectors.

        Args:
            vectors: List of vectors
            metadata_list: Optional list of metadata
            ids: Optional list of IDs
            collection: Collection name (uses default if not specified)

        Returns:
            List of inserted vector IDs
        """
        collection = collection or self.collection
        response = self._request(
            "POST",
            f"/collections/{collection}/insert_batch",
            json_data={
                "vectors": vectors,
                "metadata_list": metadata_list,
                "ids": ids
            }
        )
        return response["ids"]

    def search(
        self,
        vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        ef: Optional[int] = None,
        collection: Optional[str] = None,
        include_vectors: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            vector: Query vector
            top_k: Number of results
            filters: Optional metadata filters
            ef: HNSW search parameter
            collection: Collection name (uses default if not specified)
            include_vectors: Whether to include vector data in results

        Returns:
            List of search results
        """
        collection = collection or self.collection
        response = self._request(
            "POST",
            f"/collections/{collection}/search",
            json_data={
                "vector": vector,
                "top_k": top_k,
                "filters": filters,
                "ef": ef
            }
        )

        results = response["results"]

        # Optionally remove vectors from results
        if not include_vectors:
            for result in results:
                result.pop("vector", None)

        return results

    def get(
        self,
        id: str,
        collection: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a vector by ID.

        Args:
            id: Vector ID
            collection: Collection name (uses default if not specified)

        Returns:
            Vector data
        """
        collection = collection or self.collection
        return self._request(
            "GET",
            f"/collections/{collection}/vectors/{id}"
        )

    def delete(
        self,
        id: str,
        collection: Optional[str] = None
    ) -> bool:
        """
        Delete a vector by ID.

        Args:
            id: Vector ID
            collection: Collection name (uses default if not specified)

        Returns:
            True if deleted successfully
        """
        collection = collection or self.collection
        response = self._request(
            "DELETE",
            f"/collections/{collection}/vectors/{id}"
        )
        return response["success"]

    def stats(self, collection: Optional[str] = None) -> Dict[str, Any]:
        """
        Get collection statistics.

        Args:
            collection: Collection name (uses default if not specified)

        Returns:
            Statistics dictionary
        """
        collection = collection or self.collection
        return self._request(
            "GET",
            f"/collections/{collection}/stats"
        )

    def close(self):
        """Close the client session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
