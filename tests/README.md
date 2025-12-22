# Market Scanner - Unit Tests

## Overview
Comprehensive unit testing suite for the Market Scanner application.

## Test Coverage

### 1. Indicator Calculations (`TestIndicatorCalculations`)
- ✅ RSI calculation
- ✅ RSI with insufficient data
- ✅ ATR calculation
- ✅ Volatility calculation

### 2. Data Processing (`TestDataProcessing`)
- ✅ Portfolio profit calculation
- ✅ ROI calculation
- ✅ Target percentage calculation

### 3. Market Analysis (`TestMarketAnalysis`)
- ✅ VIX status classification (Perfect/Normal/Tension/Panic)
- ✅ SKEW status classification
- ✅ Market analysis HTML generation

### 4. HTML Generation (`TestHTMLGeneration`)
- ✅ Macro explainer generation
- ✅ Event impact descriptions

### 5. Data Validation (`TestDataValidation`)
- ✅ Empty dataframe handling
- ✅ NaN value handling
- ✅ Invalid symbol handling

### 6. Utility Functions (`TestUtilityFunctions`)
- ✅ Percentage formatting
- ✅ Currency formatting
- ✅ Date formatting

### 7. Integration Scenarios (`TestIntegrationScenarios`)
- ✅ Data fetch mocking
- ✅ Full dashboard generation flow

## Running Tests

### Install Test Dependencies
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
pytest
```

### Run with Coverage Report
```bash
pytest --cov=. --cov-report=html
```

### Run Specific Test Class
```bash
pytest tests/test_market_scanner.py::TestIndicatorCalculations
```

### Run Specific Test
```bash
pytest tests/test_market_scanner.py::TestIndicatorCalculations::test_rsi_calculation
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Only Unit Tests
```bash
pytest -m unit
```

### Run Only Integration Tests
```bash
pytest -m integration
```

## Coverage Report

After running tests with coverage, open the HTML report:
```bash
open htmlcov/index.html
```

## Test Structure

```
tests/
├── __init__.py
├── test_market_scanner.py       # Main test suite
└── README.md                     # This file
```

## Writing New Tests

### Example Test
```python
def test_new_feature(self):
    """Test description."""
    # Arrange
    input_data = [1, 2, 3]
    
    # Act
    result = my_function(input_data)
    
    # Assert
    self.assertEqual(result, expected_value)
```

### Using Mocks
```python
@patch('module.function')
def test_with_mock(self, mock_function):
    """Test with mocked dependency."""
    mock_function.return_value = 'mocked_value'
    result = function_that_uses_dependency()
    self.assertEqual(result, 'expected')
```

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements-test.txt
    pytest --cov=. --cov-report=xml
```

## Best Practices

1. **Test Naming**: Use descriptive names starting with `test_`
2. **Arrange-Act-Assert**: Follow AAA pattern
3. **Isolation**: Each test should be independent
4. **Mocking**: Mock external dependencies (API calls, file I/O)
5. **Coverage**: Aim for >80% code coverage
6. **Documentation**: Add docstrings to all tests

## Troubleshooting

### Import Errors
If you get import errors, ensure the parent directory is in the path:
```python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### Mock Not Working
Ensure you're patching the correct path:
```python
# Patch where it's used, not where it's defined
@patch('market_scanner.yf.download')  # ✅ Correct
@patch('yfinance.download')            # ❌ Wrong
```

## Future Enhancements

- [ ] Add performance benchmarking tests
- [ ] Add end-to-end browser tests
- [ ] Add API integration tests with real endpoints
- [ ] Add stress tests for large datasets
- [ ] Add security tests for PIN validation
