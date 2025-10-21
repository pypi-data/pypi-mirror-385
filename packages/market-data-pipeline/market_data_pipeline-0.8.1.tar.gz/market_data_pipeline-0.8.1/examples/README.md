# Pipeline Spec Examples

This folder contains ready-to-run **JSON specs** for the Market Data Pipeline.
They demonstrate how to spin up pipelines using the CLI or API without changing code.

---

## Available Specs

### `synthetic.json`
- **Source**: Synthetic tick generator
- **Symbols**: NVDA, SPY, QQQ
- **Duration**: 15 seconds
- **Operator**: Bars (OHLCV aggregation)
- **Sink**: Store (TimescaleDB)

Use this for a quick sanity check — it generates fake ticks and writes aggregated bars to the database.

---

### `ibkr.json`
- **Source**: Interactive Brokers (IBKR)
- **Symbols**: AAPL, MSFT, TSLA
- **Duration**: indefinite (runs until stopped)
- **Operator**: Bars
- **Sink**: Store (TimescaleDB)

Use this for live data ingestion (requires IBKR credentials + `market_data_core` integration).

---

### `replay.json`
- **Source**: Replay from historical tick data
- **File**: `data/sample_ticks.parquet` (provide your own)
- **Duration**: 30 seconds
- **Operator**: Bars
- **Sink**: Store

Use this to test pipelines deterministically from historical market data.

---

## Running Examples

### CLI

```bash
# Synthetic example
python -m market_data_pipeline.runners.cli runspec --spec examples/synthetic.json

# IBKR example
python -m market_data_pipeline.runners.cli runspec --spec examples/ibkr.json

# Replay example
python -m market_data_pipeline.runners.cli runspec --spec examples/replay.json
```

### API

```bash
# Start API server
docker compose up mdp-api -d

# Create pipeline from synthetic.json
curl -X POST http://localhost:8083/pipelines/spec \
  -H "Content-Type: application/json" \
  -d @examples/synthetic.json

# List pipelines
curl http://localhost:8083/pipelines
```

---

## Notes

- Specs are validated against `pipeline_spec.schema.json`
- Override defaults in the JSON files to tune rate, batch size, lateness, sink settings, etc.
- Ensure your database is running and `DATABASE_URL` is set for store sinks
- For IBKR examples, ensure you have the required dependencies installed
- For replay examples, provide your own historical data files

---

## Advanced Examples

Check the `examples/specs/` directory for more detailed examples including:
- High-frequency trading configurations
- Options chain processing
- Kafka sink configurations
- Production-ready settings
