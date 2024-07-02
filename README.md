# ioi-engine

In the FIX (Financial Information eXchange) protocol, *indications of interest* (IOIs) are messages used by market participants to express a non-binding interest in buying or selling a specific security.

IOIs are used to gauge market interest between brokers and clients  without committing to a trade and typically includes details like security identifier, side (buy/sell), quantity, and price (optional).

This project aims to provide a simple API to be able to automate IOI management bundled with a Redis cache.

## Usage
```bash
fastapi run ioi/ioi.py
```

### Submit
```bash
curl --header "Content-Type: application/json" \
     --request POST \
     --data '{"symbol": "TSLA",
              "side": "B",
              "ioi_shares": 100000,
              "price": 420.69}' \
     http:/localhost:8000/api/v1/ioi/submit
```

### List
```bash
curl --header "Content-Type: application/json" \
     --request GET \
     http:/localhost:8000/api/v1/ioi/list
```