# ioi-engine

In the FIX (Financial Information eXchange) protocol, *indications of interest* (IOIs) are messages used by market participants to express a non-binding interest in buying or selling a specific security.

IOIs are used to gauge market interest between brokers and clients  without committing to a trade and typically includes details like security identifier, side (buy/sell), quantity, and price (optional).

This project aims to provide a simple API to be able to automate IOI management.

## Usage
```bash
fastapi dev ioi/ioi.py
```

```bash
curl --header "Content-Type: application/json" \
     --request POST \
     --data '{"ioi_id": "1",
              "ioi_trans_type": "N",
              "symbol": "TSLA",
              "side": "B",
              "ioi_shares": 100000}' \
     http:/0.0.0.0:8000/api/submit
```
