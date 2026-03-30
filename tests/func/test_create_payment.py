import random
import uuid

import requests


def test_basic(payment):
    idempotency_key = uuid.uuid4().hex
    p = payment.create(
        total=100.12,
        currency='rub',
        description="some description",
        meta={"meta_key_1": "meta_value_1"},
        webhook_url=f'http://payment-webhook-mock:9999/api/v1/webhook/{random.randint(1, 1000)}/0',
        idempotency_key=idempotency_key,
    )
    p.data["status"] = "succeeded"
    p.wait(p.get)


def test_create_payment_same_idempotency_key(payment):
    idempotency_key = uuid.uuid4().hex
    p = payment.create(
        total=100.12,
        currency='rub',
        description="some description",
        meta={"meta_key_1": "meta_value_1"},
        webhook_url=f'http://payment-webhook-mock:9999/api/v1/webhook/{random.randint(1,1000)}/0',
        idempotency_key=idempotency_key,
    )
    p.data["status"] = "succeeded"
    p.wait(p.get)

    # create with same idempotency_key -> 409
    payment.create(
        total=100.12,
        currency='rub',
        description="some description",
        meta={"meta_key_1": "meta_value_1"},
        webhook_url=f'http://payment-webhook-mock:9999/api/v1/webhook/{random.randint(1,1000)}/0',
        idempotency_key=idempotency_key,
        return_code=requests.codes.conflict,
    )


def test_create_payment_failed_webhook(payment):
    idempotency_key = uuid.uuid4().hex
    p = payment.create(
        total=100.12,
        currency='rub',
        description="some description",
        meta={"meta_key_1": "meta_value_1"},
        webhook_url=f'http://payment-webhook-mock:9999/api/v1/webhook/{random.randint(1,1000)}/2',
        idempotency_key=idempotency_key,
    )
    p.wait(p.get)
