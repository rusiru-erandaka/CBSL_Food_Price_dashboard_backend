# Sri Lankan Food Price Analytics Platform Backend

Production-oriented FastAPI backend for historical food price analytics, public APIs, forecasting, and future environmental and AI-driven insights.

## Architecture

This codebase follows a lightweight Clean Architecture approach:

- `api/`: HTTP layer only. Routes validate requests, call services, and return response schemas.
- `services/`: Business logic. Analytics, trend generation, and forecasting orchestration live here.
- `repositories/`: Data access layer. External data sources are loaded here and exposed through repository interfaces.
- `domain/`: Core entities and contracts. Repository and forecasting abstractions are defined here.
- `forecasting/`: Pluggable forecast providers. New models can be added without changing route code.
- `transformers/`: Dataset transformation logic. The wide Hugging Face CSV is normalized into analytical long-form tables here.
- `core/`: Configuration, logging, and exception handling.
- `schemas/`: Pydantic request and response models for API contracts.
- `tests/`: Unit and API tests.

## Folder Structure

```text
app/
├── api/v1/
├── core/
├── domain/
├── forecasting/
├── repositories/
├── schemas/
├── services/
├── tests/
└── transformers/
```

## Data Flow

1. `HuggingFaceRepository` downloads the dataset file using the Hugging Face Hub SDK with:
   - `HF_DATASET_ID`
   - `HF_DATASET_FILE`
2. `DatasetNormalizer` converts wide price columns into long-form records:
   - `date`
   - `food`
   - `market`
   - `price_type`
   - `price`
3. Rainfall columns are normalized into a separate analytical table:
   - `date`
   - `rainfall_location`
   - `rainfall_mm`
4. Services consume only normalized data.
5. Forecast routes delegate forecasting to provider implementations selected by model name.

## API Endpoints

All routes are versioned under `/api/v1`.

- `GET /api/v1/health`
- `GET /api/v1/foods`
- `GET /api/v1/markets`
- `GET /api/v1/price-types`
- `GET /api/v1/foods/{food_name}`
- `GET /api/v1/foods/{food_name}/trends`
- `GET /api/v1/foods/{food_name}/statistics`
- `GET /api/v1/foods/{food_name}/forecast`
- `GET /api/v1/compare-markets`
- `GET /api/v1/compare-foods`
- `GET /api/v1/rainfall-correlation`

Interactive documentation:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Development Setup

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy the environment template and set the dataset source:

```bash
cp .env.example .env
```

4. Start the API locally:

```bash
uvicorn app.main:app --reload
```

## Testing

Run the full test suite with:

```bash
pytest app/tests
```

The test suite covers:

- dataset normalization
- food discovery
- trend generation
- statistics and comparisons
- forecasting
- request validation
- repository integration behavior

## Adding a New Forecasting Model

1. Create a provider in `app/forecasting/`.
2. Implement the `ForecastProvider` interface from `app/domain/interfaces/forecast_provider.py`.
3. Register the provider in `build_service_container()` inside `app/api/v1/dependencies.py`.
4. Reuse the existing forecast route. No route changes are required.

Example extension targets:

- `ProphetForecastProvider`
- `XGBoostForecastProvider`
- `LightGBMForecastProvider`
- `LSTMForecastProvider`
- `TransformerForecastProvider`

## Adding a New Repository

1. Implement `DatasetRepository` from `app/domain/interfaces/repository.py`.
2. Return normalized price and rainfall datasets from the new source.
3. Swap the repository instance inside `build_service_container()`.
4. Keep the service layer unchanged.

Typical future implementations:

- `PostgreSQLRepository`
- `DuckDBRepository`
- `ParquetRepository`

## Logging and Error Handling

- Structured JSON logging is configured in `app/core/logging.py`.
- Custom application exceptions are defined in `app/core/exceptions.py`.
- Request validation errors are normalized into structured API responses.

Error format:

```json
{
  "error": "FoodNotFoundError",
  "message": "Tomato not found"
}
```

## Deployment to Vercel

This repository is configured for Vercel serverless deployment through `vercel.json`.

### Deployment Steps

1. Push the repository to GitHub.
2. Import the repository into Vercel.
3. Set the environment variables in the Vercel dashboard:
   - `APP_NAME`
   - `API_VERSION`
   - `DEBUG`
   - `HF_DATASET_ID`
   - `HF_DATASET_FILE`
   - `REQUEST_TIMEOUT_SECONDS`
   - `DATASET_CACHE_TTL_SECONDS`
4. Deploy.

### Notes

- The backend uses in-memory caching within the lifetime of each serverless instance.
- Cold starts will trigger a fresh dataset fetch when the cache is empty or expired.

## Contribution Guide

When contributing:

- keep route handlers thin
- add business logic in services
- add data source logic in repositories
- add new models through forecasting providers
- maintain full type hints and tests
- prefer small, focused pull requests

## Tech Stack

- Python 3.12
- FastAPI
- Pandas
- NumPy
- Scikit-Learn
- Pydantic v2
- Uvicorn
- Pytest
- Hugging Face Hub SDK
