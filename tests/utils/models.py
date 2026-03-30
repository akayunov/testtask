import time

import requests


class EqualToAll:
    def __eq__(self, other):
        return True


equall_to_all = EqualToAll()


class Model:
    def __init__(self, session):
        self.host = "payment"
        self.port = "8888"
        self.session = session
        self.session.headers.update({'X-API-Key': 'secret_x_api_key', 'User-Agent': 'PaymentTestClient/1.0'})

    def wait(self, fn, timeout= 30, *args, **kwargs):
        start_time = time.time()
        while True:
            try:
                fn(*args, **kwargs)
                if time.time() - start_time > timeout:
                    break
            except AssertionError:
                if time.time() - start_time > timeout:
                    raise
            else:
                break
            time.sleep(0.5)


class Payment(Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = f"http://{self.host}:{self.port}/api/v1/payments"
        self.data = {}

    def create(
        self, total, currency, description, meta, webhook_url, idempotency_key, return_code=requests.codes.accepted
    ):
        self.data = {
            "total": total,
            "currency": currency,
            "description": description,
            "meta": meta,
            "webhook_url": webhook_url,
        }
        response = self.session.post(self.url, headers={"Idempotency-Key": idempotency_key}, json=self.data)
        assert response.status_code == return_code
        if return_code < 300:
            resp_json = response.json()
            print(f"Payment POST -> {resp_json}")
            self.data["id"] = resp_json["id"]
            self.data["status"] = resp_json["status"]
            self.data["created_at"] = resp_json["created_at"]
            self.data["idempotency_key"] = idempotency_key
        return self

    def get(self, return_code=requests.codes.ok):
        response = self.session.get(f"{self.url}/{self.data['id']}")
        assert response.status_code == return_code
        resp_json = response.json()
        print(f"Payment GET -> {resp_json}")
        assert resp_json['id'] == self.data['id']
        assert resp_json['total'] == str(self.data['total'])
        assert resp_json['currency'] == self.data['currency']
        assert resp_json['description'] == self.data['description']
        assert resp_json['meta'] == self.data['meta']
        assert resp_json['status'] == self.data['status']
        assert resp_json['idempotency_key'] == self.data['idempotency_key']
        assert resp_json['webhook_url'] == self.data['webhook_url']
        assert (
            resp_json['created_at'] == self.data['created_at']
        )  # assert resp_json['proceeded_at'] == self.data['proceeded_at']
