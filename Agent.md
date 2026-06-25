# Project Handoff For Coding Agents

This repository is a FastAPI backend for Sri Lankan food price analytics. It is a read-only API over a remote CSV dataset hosted on Hugging Face. There is no database, no authentication layer, and no background job system.

## What This Project Does

- Serves catalog endpoints for foods, markets, and price types.
- Returns historical trend data for a selected food, market, and price type.
- Computes descriptive statistics over filtered time ranges.
- Compares latest prices across markets or across foods.
- Computes rainfall correlation against a filtered food price series.
- Produces forecasts using pluggable forecast providers.

## Stack

- Python 3.12
- FastAPI
- Pydantic v2
- Pandas
- NumPy
- scikit-learn
- Hugging Face Hub SDK
- Uvicorn
- Pytest

## Runtime Entry Points

- Local app import path: `app.main:app`
- Root shim for some deploy targets: `main.py`
- Vercel target: `app/main.py`

## High-Level Architecture

The project follows a lightweight clean-architecture split:

- `app/main.py`: FastAPI app factory, middleware, router registration, lifespan setup.
- `app/api/v1/`: HTTP layer only. Thin route handlers, dependency injection, response shaping.
- `app/services/`: Business logic over normalized data.
- `app/repositories/`: Data access. Currently only Hugging Face CSV loading.
- `app/transformers/`: Raw dataset normalization into analytical tables.
- `app/domain/`: Core entities and interfaces.
- `app/forecasting/`: Forecast model providers.
- `app/schemas/`: Pydantic request and response contracts.
- `app/core/`: Config, logging, exceptions, text normalization helpers.
- `app/tests/`: In-memory repository based tests.

## Core Request Flow

Normal request path:

1. FastAPI route receives request.
2. Query params are validated by Pydantic models in `app/schemas/requests.py`.
3. Route resolves a service via dependency functions in `app/api/v1/dependencies.py`.
4. Service calls the repository for normalized data.
5. Repository loads or reuses cached DataFrames.
6. Service filters, aggregates, correlates, or forecasts.
7. Route maps domain objects to response schemas in `app/schemas/responses.py`.

## Dependency Injection Pattern

The app stores a `ServiceContainer` on `app.state.container`.

Container contents:

- `repository`
- `food_service`
- `trend_service`
- `analytics_service`
- `forecast_service`

Container assembly happens in `build_service_container()` in `app/api/v1/dependencies.py`.

## Data Source

Current source: Hugging Face dataset repository.

Configured by:

- `HF_DATASET_ID`
- `HF_DATASET_FILE`

The repository implementation is `HuggingFaceRepository` in `app/repositories/huggingface_repository.py`.

Behavior:

- Downloads the configured CSV with `hf_hub_download`.
- Reads it with `pandas.read_csv`.
- Normalizes it once through `DatasetNormalizer`.
- Caches normalized price and rainfall DataFrames in memory.
- Reloads when cache is empty or TTL expires.

Important caching behavior:

- `DATASET_CACHE_TTL_SECONDS=0` means reload every access.
- Positive TTL means in-memory caching per process lifetime.
- In serverless environments this cache is instance-local only.

## Normalized Data Model

The raw CSV is expected to contain:

- A `date` column.
- Wide price columns like `retail_pettah_Tomato`.
- Optional rainfall columns like `rainfall_nuwara_eliya_mm`.

`DatasetNormalizer` converts the CSV into two long-form tables.

Price table columns:

- `date`
- `food`
- `market`
- `price_type`
- `price`

Rainfall table columns:

- `date`
- `rainfall_location`
- `rainfall_mm`

Important normalizer details:

- Invalid or missing dates are dropped.
- Non-numeric price and rainfall values are coerced and dropped if null.
- Foods and markets are inferred by splitting wide column names on `_`.
- `humanize_label()` title-cases labels like `nuwara_eliya` -> `Nuwara Eliya`.
- Rainfall columns are detected only if they match `rainfall_*_mm`.

## API Surface

All versioned endpoints live under `/api/v1`.

Catalog:

- `GET /api/v1/foods`
- `GET /api/v1/markets`
- `GET /api/v1/price-types`
- `GET /api/v1/foods/{food_name}`

Trends:

- `GET /api/v1/foods/{food_name}/trends`
  - Query: `market`, `price_type`, `time_range`

Analytics:

- `GET /api/v1/foods/{food_name}/statistics`
  - Query: `market`, `price_type`, `time_range`
- `GET /api/v1/compare-markets`
  - Query: `food`, `price_type`
- `GET /api/v1/compare-foods`
  - Query: `market`, `price_type`
- `GET /api/v1/rainfall-correlation`
  - Query: `food`, `market`, `price_type`

Forecasting:

- `GET /api/v1/foods/{food_name}/forecast`
  - Query: `market`, `price_type`, `days_ahead`, `model`

Other:

- `GET /api/v1/health`
- `GET /debug`

Docs:

- `/docs`
- `/redoc`

## Query Contracts

Time range enum values:

- `7d`
- `30d`
- `3m`
- `6m`
- `1y`
- `2y`
- `all`

Forecast constraints:

- `days_ahead` default: `7`
- `days_ahead` min: `1`
- `days_ahead` max: `90`
- `model` default: `moving_average`

Validation is strict because the Pydantic models use `extra="forbid"`.

## Name Resolution Rules

Food names, markets, and price types are matched case-insensitively through helpers in `app/services/_utils.py`.

Examples:

- `tomato` matches `Tomato`
- `pettah` matches `Pettah`
- `retail` matches `retail`

Matching is whitespace and underscore tolerant because keys are normalized through `normalize_key()`.

## Service Responsibilities

### `FoodService`

- Returns discovered foods, markets, and price types.
- Returns per-food metadata:
  - available markets
  - available price types

### `TrendService`

- Filters the normalized dataset by:
  - food
  - market
  - price type
  - time range
- Returns ordered `(date, price)` points.

### `AnalyticsService`

- `get_statistics()`
  - min
  - max
  - average
  - current price
  - percent change from first to last point
  - population std-dev as volatility
- `compare_markets()`
  - latest row per market for one food and one price type
- `compare_foods()`
  - latest row per food for one market and one price type
- `calculate_rainfall_correlation()`
  - merges price series against each rainfall location by `date`
  - computes Pearson correlation
  - returns the correlation with the strongest absolute value

### `ForecastService`

- Resolves food, market, and price type.
- Selects a provider by model name.
- Passes the filtered series to that provider.
- Returns forecast points with future dates.

## Forecast Providers

Current providers registered in the container:

- `moving_average`
- `linear_regression`

### `moving_average`

- Uses the last `window_size` prices.
- Defaults to a 7-point window in production container wiring.
- Returns the same predicted value for all future dates.

### `linear_regression`

- Converts dates to day offsets from the first observed date.
- Fits `sklearn.linear_model.LinearRegression`.
- If all samples fall on the same day offset, it falls back to repeating the last price.
- Clamps negative predictions to `0.0`.

## Error Model

Custom exception classes live in `app/core/exceptions.py`.

Main structured error types:

- `FoodNotFoundError`
- `MarketNotFoundError`
- `PriceTypeNotFoundError`
- `ForecastModelNotFoundError`
- `InvalidTimeRangeError`
- `DatasetLoadError`
- `InsufficientDataError`
- `ValidationError`
- `InternalServerError`

Response shape:

```json
{
  "error": "FoodNotFoundError",
  "message": "Tomato not found"
}
```

Important behavior:

- Request validation errors are rewritten into a single string message.
- Unhandled exceptions are exposed as `500` with `str(exc)`.

## Logging

Logging is structured JSON.

Configured in:

- `app/core/logging.py`

Observed log events include:

- `application_starting`
- `application_stopping`
- `request_completed`
- `loading_dataset`
- `dataset_loaded`
- `dataset_download_failed`
- `dataset_normalization_failed`
- `forecast_execution_started`

## Configuration

Environment is loaded from `.env` via `python-dotenv`.

Primary settings:

- `APP_NAME`
- `API_VERSION`
- `DEBUG`
- `HF_DATASET_ID`
- `HF_DATASET_FILE`
- `REQUEST_TIMEOUT_SECONDS`
- `DATASET_CACHE_TTL_SECONDS`

Defaults are defined in `app/core/config.py`.

Example values are in `.env.example`.

## Current Operational Constraints

- No persistence layer beyond in-memory process cache.
- No auth or permission model.
- No write endpoints.
- No pagination.
- No async data fetching in the repository path.
- Remote dataset shape is a hard dependency; schema drift can break normalization.

## Test Strategy

Tests use an in-memory repository defined in `app/tests/conftest.py`.

Coverage areas:

- normalization
- repository behavior
- food catalog endpoints
- trends
- statistics
- rainfall correlation
- forecasts
- validation handling

## Current Test Caveat

At the time of writing, `pytest app/tests` does not start successfully unless `httpx` is installed, because `fastapi.testclient.TestClient` depends on Starlette's `TestClient`, which now requires `httpx`.

`requirements.txt` currently does not include `httpx`.

If you need the tests to run, add `httpx` to dependencies first.

## Safe Change Patterns

If adding a new forecast model:

1. Implement `ForecastProvider` in `app/forecasting/`.
2. Reuse `BaseForecastProvider` for common validation if applicable.
3. Register the provider in `build_service_container()`.
4. Keep the route contract unchanged.

If adding a new data source:

1. Implement `DatasetRepository`.
2. Return normalized price and rainfall DataFrames.
3. Replace the repository in `build_service_container()`.
4. Keep services unchanged if repository semantics remain the same.

If adding a new endpoint:

1. Add request and response schemas first if needed.
2. Put business logic in a service, not in the route.
3. Keep the route thin.
4. Raise `AppError` subclasses for known failures.
5. Add focused tests using the in-memory repository pattern.

## Things A Coding Agent Should Verify Before Editing

- Whether the requested change belongs in `api`, `services`, `repositories`, or `forecasting`.
- Whether the change assumes database behavior that does not exist here.
- Whether the raw Hugging Face dataset schema must change.
- Whether the route should preserve the current response contract.
- Whether time range filtering or case-insensitive resolution already solves the request.
- Whether a new error type is needed for structured failures.
- Whether test fixtures need to include extra columns or edge cases.

## Quick File Map

- `app/main.py`: app factory and router registration
- `app/api/v1/dependencies.py`: DI and service container
- `app/api/v1/*.py`: routes
- `app/services/_utils.py`: shared resolution and time-range filtering
- `app/services/food_service.py`: catalog logic
- `app/services/trend_service.py`: trend logic
- `app/services/analytics_service.py`: statistics, comparisons, correlation
- `app/services/forecast_service.py`: forecast orchestration
- `app/repositories/huggingface_repository.py`: remote dataset loading and caching
- `app/transformers/dataset_normalizer.py`: wide-to-long normalization
- `app/forecasting/*.py`: forecast providers
- `app/core/config.py`: env-driven settings
- `app/core/exceptions.py`: error model
- `app/schemas/requests.py`: query param contracts
- `app/schemas/responses.py`: response contracts
- `app/tests/`: behavior expectations

## Bottom Line

Treat this project as an analytical read API over normalized Pandas DataFrames. Most changes should preserve the existing layering:

- routes stay thin
- services own business logic
- repositories own data loading
- normalizers own dataset shape adaptation
- forecast providers remain pluggable

If a requested feature can be implemented by filtering or aggregating the normalized dataset in a service, that is usually the correct design.
