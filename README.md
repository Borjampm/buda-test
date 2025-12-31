# buda-test
Solution to technical problem for my application to Buda.com. The API can be found deployed at https://buda-test-483627943871.us-central1.run.app with the documentation at https://buda-test-483627943871.us-central1.run.app/docs.

## Supuestos
- El precio en tiempo real se obtiene a partir de una simulación de cotización de venta de mi portfolio.

## Installation

```bash
uv sync --frozen --no-dev
```

## How to Run

```bash
uv run uvicorn src.main:app --reload
```

## Docker

```bash
docker build -t buda-test .
docker run -p 8000:8000 buda-test
```