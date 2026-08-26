import pytest
from fastapi import status
from unittest.mock import patch, MagicMock


class TestSourceAPI:
    def _create_chest(self, client, name="Test Chest"):
        resp = client.post("/api/chests/", json={"name": name})
        return resp.json()["id"]

    def test_list_sources_empty(self, client):
        chest_id = self._create_chest(client)
        response = client.get(f"/api/sources/?chest_id={chest_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_sources_missing_chest_id(self, client):
        response = client.get("/api/sources/")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_source(self, client):
        chest_id = self._create_chest(client)
        response = client.post(
            "/api/sources/",
            json={
                "name": "My Source",
                "type": "TXT",
                "content": "Some content here",
                "chest_id": chest_id,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "My Source"
        assert data["type"] == "TXT"
        assert data["chest_id"] == chest_id
        assert data["is_enabled"] is True
        assert "id" in data

    def test_get_source(self, client):
        chest_id = self._create_chest(client)
        create_resp = client.post(
            "/api/sources/",
            json={
                "name": "Get Me",
                "type": "TXT",
                "content": "content",
                "chest_id": chest_id,
            },
        )
        source_id = create_resp.json()["id"]

        response = client.get(f"/api/sources/{source_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Get Me"

    def test_get_source_not_found(self, client):
        response = client.get("/api/sources/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_source(self, client):
        chest_id = self._create_chest(client)
        create_resp = client.post(
            "/api/sources/",
            json={
                "name": "Original",
                "type": "TXT",
                "content": "original content",
                "chest_id": chest_id,
            },
        )
        source_id = create_resp.json()["id"]

        response = client.patch(f"/api/sources/{source_id}", json={"name": "Updated"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Updated"

    def test_update_source_disable(self, client):
        chest_id = self._create_chest(client)
        create_resp = client.post(
            "/api/sources/",
            json={
                "name": "Toggle",
                "type": "TXT",
                "content": "content",
                "chest_id": chest_id,
            },
        )
        source_id = create_resp.json()["id"]

        response = client.patch(f"/api/sources/{source_id}", json={"is_enabled": False})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["is_enabled"] is False

    def test_update_source_not_found(self, client):
        response = client.patch("/api/sources/999", json={"name": "Nope"})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_source(self, client):
        chest_id = self._create_chest(client)
        create_resp = client.post(
            "/api/sources/",
            json={
                "name": "Delete Me",
                "type": "TXT",
                "content": "content",
                "chest_id": chest_id,
            },
        )
        source_id = create_resp.json()["id"]

        response = client.delete(f"/api/sources/{source_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        get_resp = client.get(f"/api/sources/{source_id}")
        assert get_resp.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_source_not_found(self, client):
        response = client.delete("/api/sources/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_url_source(self, client):
        chest_id = self._create_chest(client)
        response = client.post(
            "/api/sources/",
            json={
                "name": "URL Source",
                "type": "URL",
                "content": "https://example.com",
                "chest_id": chest_id,
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["type"] == "URL"
