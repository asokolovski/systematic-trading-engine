# systematic-trading-engine

Minimal systematic trading project with:
- a CLI backtesting demo
- a paper-trading demo
- a barebones FastAPI layer for running the default backtest over HTTP

## 1. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

## 2. Run the original CLI demo

```bash
python3 main.py
```

## 3. Run the REST API

```bash
uvicorn api.main:app --reload
```

Once the server is running, open:
- `http://127.0.0.1:8000/docs` for the interactive Swagger UI
- `http://127.0.0.1:8000/health` for a simple health check

## 4. Test the API with curl

```bash
curl -X POST http://127.0.0.1:8000/backtests/run \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "SPY",
    "start_date": "2015-01-01",
    "end_date": "2020-01-01"
  }'
```

Example request body:

```json
{
  "ticker": "SPY",
  "start_date": "2015-01-01",
  "end_date": "2020-01-01"
}
```

The API currently uses a fixed moving-average crossover strategy in code. That
keeps the contract small so you can focus on the core service flow:
- request comes in
- FastAPI validates the contract
- the backtester runs
- JSON comes back out

## 5. Run with Docker

Build the image:

```bash
docker build -t systematic-trading-engine-api .
```

Run the container:

```bash
docker run --rm -p 8000:8000 systematic-trading-engine-api
```

Then open:
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`

t