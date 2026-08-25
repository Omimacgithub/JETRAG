import pytest
from fastapi import status


class TestChestAPI:
    def test_list_chests_empty(self, client):
        response = client.get("/api/chests/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_create_chest(self, client):
        response = client.post("/api/chests/", json={"name": "My Chest"})
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "My Chest"
        assert "id" in data
        assert "created_at" in data

    def test_get_chest(self, client):
        create_resp = client.post("/api/chests/", json={"name": "Get Test"})
        chest_id = create_resp.json()["id"]

        response = client.get(f"/api/chests/{chest_id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Get Test"

    def test_get_chest_not_found(self, client):
        response = client.get("/api/chests/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Chest not found"

    def test_get_chest_invalid_id(self, client):
        response = client.get("/api/chests/abc")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_chest(self, client):
        create_resp = client.post("/api/chests/", json={"name": "Original"})
        chest_id = create_resp.json()["id"]

        response = client.patch(f"/api/chests/{chest_id}", json={"name": "Updated"})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Updated"

    def test_update_chest_not_found(self, client):
        response = client.patch("/api/chests/999", json={"name": "Nope"})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_chest(self, client):
        create_resp = client.post("/api/chests/", json={"name": "To Delete"})
        chest_id = create_resp.json()["id"]

        response = client.delete(f"/api/chests/{chest_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        get_resp = client.get(f"/api/chests/{chest_id}")
        assert get_resp.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_chest_not_found(self, client):
        response = client.delete("/api/chests/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_chests_multiple(self, client):
        client.post("/api/chests/", json={"name": "Chest A"})
        client.post("/api/chests/", json={"name": "Chest B"})
        client.post("/api/chests/", json={"name": "Chest C"})

        response = client.get("/api/chests/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_list_chests_with_pagination(self, client):
        for i in range(5):
            client.post("/api/chests/", json={"name": f"Chest {i}"})

        response = client.get("/api/chests/?skip=0&limit=2")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Welcome to JETRAG API"}
