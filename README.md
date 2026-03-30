### Payment service

#### 1) Start application in docker compose

`docker compose -f docker-compose.yml  --profile dev build`

`docker compose  -f docker-compose.yml --profile dev up --detach`

#### 2) Run tests

`docker exec -it testtask-payment-test-func-1 bash`

`pytest func`



### Examples:
```
curl -X POST http://payment:8888/api/v1/payments \
     -H "Content-Type: application/json" \
     -H "X-API-Key: secret_x_api_key" \
	 -H "Idempotency-Key: 7b2e3e4a-9b1a-4d3f-8c2d-1a2b3c4d5e6f" \
     -d '{
           "total": 123.12,
           "currency": "rub",
           "description": "some description",
           "meta": {},
           "webhook_url": "http://localhost:8888/non_exists"
         }'
```

```
curl http://payment:8888/api/v1/payments/10 -H "X-API-Key: secret_x_api_key" 
```