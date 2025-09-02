from service.common import status
from service import app
from service.models import db, Account

BASE_URL = "/accounts"

class TestAccountsREST:
    def setUp(self):
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_list_empty_returns_200_and_empty_array(self):
        resp = self.client.get(BASE_URL)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.get_json() == []

    def test_list_returns_all_accounts(self):
        self.client.post(BASE_URL, json={"name": "Ana", "email": "ana@example.com", "address": "Rua A, 123"})
        self.client.post(BASE_URL, json={"name": "Bruno", "email": "bruno@example.com", "address": "Rua B, 456"})
        resp = self.client.get(BASE_URL)
        data = resp.get_json()
        assert resp.status_code == status.HTTP_200_OK
        assert isinstance(data, list) and len(data) == 2

    def test_read_account_found_and_not_found(self):
        created = self.client.post(BASE_URL, json={"name": "Carla", "email": "carla@example.com", "address": "Av. C, 789"})
        acc_id = created.get_json()["id"]

        ok = self.client.get(f"{BASE_URL}/{acc_id}")
        assert ok.status_code == status.HTTP_200_OK
        assert ok.get_json()["email"] == "carla@example.com"

        nf = self.client.get(f"{BASE_URL}/0")
        assert nf.status_code == status.HTTP_404_NOT_FOUND

    def test_update_account_found_and_not_found(self):
        created = self.client.post(BASE_URL, json={"name": "Diego", "email": "diego@example.com", "address": "Rua D, 000"})
        acc_id = created.get_json()["id"]

        payload = {"name": "Diego Silva", "email": "diego@example.com", "address": "Rua Nova, 111"}
        up = self.client.put(f"{BASE_URL}/{acc_id}", json=payload)
        assert up.status_code == status.HTTP_200_OK
        assert up.get_json()["name"] == "Diego Silva"
        assert up.get_json()["address"] == "Rua Nova, 111"

        nf = self.client.put(f"{BASE_URL}/424242", json=payload)
        assert nf.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_is_idempotent_and_returns_204(self):
        created = self.client.post(BASE_URL, json={"name": "Eva", "email": "eva@example.com", "address": "Rua E, 222"})
        acc_id = created.get_json()["id"]

        res1 = self.client.delete(f"{BASE_URL}/{acc_id}")
        assert res1.status_code == status.HTTP_204_NO_CONTENT
        assert res1.data == b""

        res2 = self.client.delete(f"{BASE_URL}/{acc_id}")
        assert res2.status_code == status.HTTP_204_NO_CONTENT
        assert res2.data == b""
