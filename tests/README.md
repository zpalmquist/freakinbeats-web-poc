# Test Suite

Comprehensive tests for Freakinbeats Web application with 99% coverage of critical sync service.

## Quick Start

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/services/ --cov=app.services.discogs_sync_service --cov-report=term

# Watch mode (auto-rerun on changes)
pytest-watch tests/
```

## Structure

```
tests/
├── conftest.py                      # Shared fixtures (app, db, sync_service)
├── fetch_real_discogs_data.py       # Utility: fetch real API samples
├── services/
│   ├── test_discogs_sync_service.py # 26 unit tests (mock data)
│   └── test_real_discogs_data.py    # 7 integration tests (real API data)
└── fixtures/
    ├── discogs_factory.py           # Mock data generator (Faker)
    └── real_discogs_data.json       # Real API samples (git-ignored)
```

## Tools

| Tool | Purpose |
|------|---------|
| pytest | Test framework |
| pytest-flask | Flask test helpers |
| pytest-cov | Coverage reporting |
| Faker | Realistic mock data generation |
| responses | HTTP request mocking |
| freezegun | Time manipulation |

## Coverage

**99% code coverage** on `DiscogsSyncService`
- ✅ 33 passing tests
- ✅ API fetching (success, errors, pagination)
- ✅ Database sync (add, update, remove)
- ✅ Data transformation
- ✅ Error handling & recovery

## Configuration

### Environment Variables

```bash
# Optional: Enable real API data validation tests
ENABLE_REAL_DATA_TESTS=true
```

### Real Data Tests (Optional)

By default, tests use mock data. To validate against real Discogs API:

```bash
# 1. Enable in .env
export ENABLE_REAL_DATA_TESTS=true

# 2. Fetch minimal sample (3 listings)
python3 tests/fetch_real_discogs_data.py

# 3. Run tests
pytest tests/services/ -v
```

Real data tests are **skipped by default** to keep tests fast and not require API access.

## Key Fixtures

```python
app           # Flask app with test config
db            # Clean in-memory SQLite per test
session       # Database session
sync_service  # Configured DiscogsSyncService
discogs_factory  # Mock data generator
```

## CI/CD

```yaml
- name: Run Tests
  run: pytest tests/ -v --cov=app.services.discogs_sync_service --cov-fail-under=95
```

## Notes

- `real_discogs_data.json` is git-ignored (contains minimal API samples)
- Tests use in-memory SQLite for speed and isolation
- Mock data factory generates reproducible test data (seed=42)
- Real data tests validate against actual API structure
