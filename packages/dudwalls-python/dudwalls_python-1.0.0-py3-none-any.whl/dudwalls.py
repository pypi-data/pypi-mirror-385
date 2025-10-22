import requests
import json
from typing import Dict, List, Any, Optional

class Dudwalls:
    def __init__(self, api_key: str, base_url: str = "https://dudwalls.me/api/dudwalls"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        
        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data if data else None
        )
        
        if not response.ok:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        return response.json()

    def get_databases(self) -> List[Dict]:
        return self._request("GET", "")

    def create_database(self, name: str) -> Dict:
        return self._request("POST", "", {"name": name})

    def collection(self, database: str, collection: str) -> 'Collection':
        return Collection(self, database, collection)

class Collection:
    def __init__(self, client: Dudwalls, database: str, collection: str):
        self.client = client
        self.database = database
        self.collection = collection
        self.base_path = f"/{database}/{collection}"

    def find(self, query: Dict = None) -> List[Dict]:
        params = f"?{requests.compat.urlencode(query)}" if query else ""
        return self.client._request("GET", f"{self.base_path}{params}")

    def find_one(self, doc_id: str) -> Dict:
        return self.client._request("GET", f"{self.base_path}/{doc_id}")

    def insert_one(self, document: Dict) -> Dict:
        return self.client._request("POST", self.base_path, document)

    def insert_many(self, documents: List[Dict]) -> Dict:
        return self.client._request("POST", f"{self.base_path}/bulk", {"documents": documents})

    def update_one(self, doc_id: str, update: Dict) -> Dict:
        return self.client._request("PUT", f"{self.base_path}/{doc_id}", update)

    def delete_one(self, doc_id: str) -> Dict:
        return self.client._request("DELETE", f"{self.base_path}/{doc_id}")

    def count(self) -> Dict:
        return self.client._request("GET", f"{self.base_path}/count")
