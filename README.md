# buda-test
Solution to technical problem for my application to Buda.com

## Supuestos
- El precio de una última orden ejecutada se obtiene a partir de una simulación de cotización de mi portfolio.

## Installation

## How to Run

```bash
uv run uvicorn src.main:app --reload
```

## Docker

```bash
docker build -t buda-test .
docker run -p 8000:8000 buda-test
```